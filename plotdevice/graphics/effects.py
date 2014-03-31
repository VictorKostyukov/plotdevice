# encoding: utf-8
import os
import re
from contextlib import contextmanager
from AppKit import *
from Foundation import *
from Quartz import *

from plotdevice import DeviceError
from ..util import _copy_attr, _copy_attrs
from .colors import Color

_ctx = None
__all__ = ("Effect", "Shadow", "Mask",)

# blend modes
_BLEND=dict(
    # basics
    normal=kCGBlendModeNormal,
    clear=kCGBlendModeClear,
    copy=kCGBlendModeCopy,

    # pdf
    multiply=kCGBlendModeMultiply,
    screen=kCGBlendModeScreen,
    overlay=kCGBlendModeOverlay,
    darken=kCGBlendModeDarken,
    lighten=kCGBlendModeLighten,
    colordodge=kCGBlendModeColorDodge,
    colorburn=kCGBlendModeColorBurn,
    softlight=kCGBlendModeSoftLight,
    hardlight=kCGBlendModeHardLight,
    difference=kCGBlendModeDifference,
    exclusion=kCGBlendModeExclusion,
    hue=kCGBlendModeHue,
    saturation=kCGBlendModeSaturation,
    color=kCGBlendModeColor,
    luminosity=kCGBlendModeLuminosity,

    # nextstep
    sourcein=kCGBlendModeSourceIn,
    sourceout=kCGBlendModeSourceOut,
    sourceatop=kCGBlendModeSourceAtop,
    destinationover=kCGBlendModeDestinationOver,
    destinationin=kCGBlendModeDestinationIn,
    destinationout=kCGBlendModeDestinationOut,
    destinationatop=kCGBlendModeDestinationAtop,
    xor=kCGBlendModeXOR,
    plusdarker=kCGBlendModePlusDarker,
    pluslighter=kCGBlendModePlusLighter,
)

BLEND_MODES = """    normal, clear, copy, xor, multiply, screen,
    overlay, darken, lighten, difference, exclusion,
    color-dodge, color-burn, soft-light, hard-light,
    hue, saturation, color, luminosity,
    source-in, source-out, source-atop, plusdarker, pluslighter
    destination-over, destination-in, destination-out, destination-atop"""


@contextmanager
def _ns_context():
    ctx = NSGraphicsContext.currentContext()
    ctx.saveGraphicsState()
    yield ctx
    ctx.restoreGraphicsState()

@contextmanager
def _cg_context():
    port = NSGraphicsContext.currentContext().graphicsPort()
    CGContextSaveGState(port)
    yield port
    CGContextRestoreGState(port)

@contextmanager
def _cg_layer():
    # CGContextBeginTransparencyLayerWithRect(_cg_port(), <bounds>, None)
    CGContextBeginTransparencyLayer(_cg_port(), None)
    yield
    CGContextEndTransparencyLayer(_cg_port())

def _cg_port():
    return NSGraphicsContext.currentContext().graphicsPort()

class Frob(object):
    """A FoRmatting OBject encapsulates changes to the graphics context state.

    It can be appended to the current canvas for a one-shot change or pushed onto the
    canvas to perform a reset once the associated with block completes.
    """
    _grobs = None

    def append(self, grob):
        if self._grobs is None:
            self._grobs = []
        self._grobs.append(grob)

    def _draw(self):
        # apply state changes only to contained grobs
        with self.applied():
            for grob in self._grobs:
                grob._draw()

    @property
    def contents(self):
        return self._grobs or []

class Effect(Frob):
    kwargs = ('blend','alpha','shadow')

    def __init__(self, *args, **kwargs):
        self._fx = {}

        if args and isinstance(args[0], Effect):
            self._rollback = args[0]
            for eff, val in args[0]._fx.items():
                self._fx[eff] = val
            for eff, val in kwargs.items():
                setattr(self, eff, val)
        else:
            for eff in Effect.kwargs:
                setattr(self, eff, kwargs.get(eff))

        # just omit effects being set to their default values
        defaults = {"alpha":1.0, "blend":"normal", "shadow":None}
        for attr, default in defaults.items():
            if self._fx.get(attr) == default:
                self._fx.pop(attr, None)

    def __repr__(self):
        return 'Effect(%r)'%self._fx

    def __enter__(self):
        if not hasattr(self, '_rollback'):
            self._rollback = Effect(_ctx._effects)
        return None

    def __exit__(self, type, value, tb):
        _ctx._effects = self._rollback
        del self._rollback

    def set(self, *effs):
        """Add compositing effects to the drawing context"""

        # apply effects specified in the args (or all by default)
        if not effs:
            effs = Effect.kwargs

        fx = {k:v for k,v in self._fx.items() if k in effs}
        if 'alpha' in fx:
            CGContextSetAlpha(_cg_port(), fx['alpha']);
        if 'blend' in fx:
            CGContextSetBlendMode(_cg_port(), _BLEND[fx['blend']])
        if 'shadow' in fx:
            fx['shadow']._nsShadow.set() # don't mess with cg for shadows
            return True

    @contextmanager
    def applied(self):
        """Apply compositing effects (if any) to any drawing inside the `with` block"""
        if self._fx:
            self.set('blend', 'alpha')
            with _cg_layer():
                if not self.set('shadow'):
                    yield # if there's no shadow, we don't need a second layer
                else:
                    with _cg_layer():
                        yield # if there is, we do
        else:
            # nothing to be done
            yield

    def copy(self):
        new = Effect()
        new._fx = dict(self._fx)
        return new

    @classmethod
    def _validate(self, eff, val):
        if val is None:
            pass
        elif eff=='alpha' and not (isinstance(val, (int,float,long)) and 0<=val<=1):
            badalpha = 'alpha() value must be a number between 0 and 1.0'
            raise DeviceError(badalpha)
        elif eff=='blend':
            val = re.sub(r'[_\- ]','', val).lower()
            if val not in _BLEND:
                badblend = '"%s" is not a recognized blend mode.\nUse one of:\n%s'%(val, BLEND_MODES)
                raise DeviceError(badblend)
        elif eff=='shadow':
            if isinstance(val, Shadow):
                val = val.copy()
            else:
                val = Shadow(*val)

        return val

    def _get_alpha(self):
        return self._fx.get('alpha', 1.0)
    def _set_alpha(self, a):
        if a is None:
            self._fx.pop('alpha', None)
        else:
            self._fx['alpha'] = Effect._validate('alpha', a)
    alpha = property(_get_alpha, _set_alpha)

    def _get_blend(self):
        return self._fx.get('blend', 'normal')
    def _set_blend(self, mode):
        if mode is None:
            self._fx.pop('blend', None)
        else:
            self._fx['blend'] = Effect._validate('blend', mode)
    blend = property(_get_blend, _set_blend)

    def _get_shadow(self):
        return self._fx.get('shadow', None)
    def _set_shadow(self, spec):
        if spec is None:
            self._fx.pop('shadow', None)
        else:
            self._fx['shadow'] = Effect._validate('shadow', spec)
    shadow = property(_get_shadow, _set_shadow)

class Shadow(object):
    kwargs = ('color','blur','offset')

    def __init__(self, *args, **kwargs):
        super(Shadow, self).__init__()
        if args and isinstance(args[0], Shadow):
            self._nsShadow = _copy_attr(args[0]._nsShadow)
            for attr, val in kwargs.items():
                if attr not in Shadow.kwargs: continue
                setattr(self, attr, val)
        else:
            self._nsShadow = NSShadow.alloc().init()
            for attr, val in zip(Shadow.kwargs, args):
                kwargs.setdefault(attr, val)

            self.color = Color(kwargs['color'])
            self.blur = kwargs.get('blur', 10 if self.color.a else 0)
            offset = kwargs.get('offset', self.blur)
            if isinstance(offset, (int,float,long)):
                offset = [offset]
            if len(offset)==1:
                offset *= 2
            self.offset = offset

    def __repr__(self):
        return "Shadow(%r, blur=%r, offset=%r)" % (self.color, self.blur, tuple(self.offset))

    def copy(self):
        return Shadow(self)

    def _get_color(self):
        return Color(self._nsShadow.shadowColor())
    def _set_color(self, spec):
        if isinstance(spec, Color):
            self._nsShadow.setShadowColor_(spec.nsColor)
        elif spec is None:
            self._nsShadow.setShadowColor_(None)
        else:
            if not isinstance(spec, (tuple,list)):
                spec = tuple([spec])
            self._nsShadow.setShadowColor_(Color(*spec).nsColor)
    color = property(_get_color, _set_color)

    def _get_blur(self):
        return self._nsShadow.shadowBlurRadius()
    def _set_blur(self, blur):
        self._nsShadow.setShadowBlurRadius_(blur)
    blur = property(_get_blur, _set_blur)

    def _get_offset(self):
        x,y = self._nsShadow.shadowOffset()
        return Point(x,-y)
    def _set_offset(self, offset):
        if isinstance(offset, (int,float,long)):
            x = y = offset
        else:
            x,y = offset
        self._nsShadow.setShadowOffset_((x,-y))
    offset = property(_get_offset, _set_offset)



class Mask(Frob):
    def __init__(self, path, invert=False):
        from .bezier import Bezier
        self.path = Bezier(path)
        self.path.inherit()
        self.evenodd = invert

    def set(self):
        port = _cg_port()
        cg_path = self.path.transform.apply(self.path).cgPath

        CGContextBeginPath(port)
        if self.evenodd:
            CGContextAddRect(port, ((0,0),(_ctx.WIDTH, _ctx.HEIGHT)))
            CGContextAddPath(port, cg_path)
            CGContextEOClip(port)
        else:
            CGContextAddPath(port, cg_path)
            CGContextClip(port)


    @contextmanager
    def applied(self):
        with _cg_context():
            self.set()
            yield

class ClippingPath(Mask):
    pass # NodeBox compat...
