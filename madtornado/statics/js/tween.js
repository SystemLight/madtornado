(function () {
    // 判断是否存在帧动画函数
    if (!window.requestAnimationFrame) {
        let lastTime = 0;
        window.requestAnimationFrame = function (callback) {
            let nowTime = Date.now();
            let delay = Math.max(0, 16.7 - (nowTime - lastTime));
            lastTime = nowTime;
            return setTimeout(callback, delay);
        };
        window.cancelAnimationFrame = function (index) {
            clearTimeout(index);
        };
    }
})();

function LsTween(op) {
    let el = op["el"];
    let attr = op["attr"];
    let fx = op.fx || "easeOut";
    let duration = op.duration || 400;
    let maxC = 0;
    if (el.animationTimer) {
        return;
    }
    let t = 0;
    let b = {};
    let c = {};
    for (let s in attr) {
        if (attr.hasOwnProperty(s)) {
            b[s] = LsTween.css(el, s);
            c[s] = attr[s] - b[s];
            maxC = Math.max(maxC, Math.abs(c[s]));
        }
    }
    if (typeof duration === "object") {
        let durationOption = duration;
        durationOption.multiple = durationOption.multiple || 2;
        duration = maxC * duration.multiple;
        duration = durationOption.max ? Math.min(duration, durationOption.max) : duration;
        duration = durationOption.min ? Math.max(duration, durationOption.min) : duration;
    }

    // requestAnimationFrame认为每秒有60帧，计算持续时间内有多少帧
    let d = Math.ceil(duration / (1000 / 60));
    move();

    function move() {
        el.animationTimer = requestAnimationFrame(function () {
            t++;
            if (t > d) {
                el.animationTimer = 0;
                op["cb"] && op["cb"]();
            } else {
                for (let s in attr) {
                    if (attr.hasOwnProperty(s)) {
                        let val = LsTween.tween[fx](t, b[s], c[s], d);
                        LsTween.css(el, s, val);
                        op["move"] && op["move"]();
                    }
                }
                move();
            }
        });
    }
}

// t:当前帧第几帧，b:开始值，c:总值，d:总帧数
LsTween.tween = {
    linear: function (t, b, c, d) {  //匀速
        return c * t / d + b;
    },
    easeIn: function (t, b, c, d) {  //加速曲线
        return c * (t /= d) * t + b;
    },
    easeOut: function (t, b, c, d) {  //减速曲线
        return -c * (t /= d) * (t - 2) + b;
    },
    easeBoth: function (t, b, c, d) {  //加速减速曲线
        if ((t /= d / 2) < 1) {
            return c / 2 * t * t + b;
        }
        return -c / 2 * ((--t) * (t - 2) - 1) + b;
    },
    easeInStrong: function (t, b, c, d) {  //加加速曲线
        return c * (t /= d) * t * t * t + b;
    },
    easeOutStrong: function (t, b, c, d) {  //减减速曲线
        return -c * ((t = t / d - 1) * t * t * t - 1) + b;
    },
    easeBothStrong: function (t, b, c, d) {  //加加速减减速曲线
        if ((t /= d / 2) < 1) {
            return c / 2 * t * t * t * t + b;
        }
        return -c / 2 * ((t -= 2) * t * t * t - 2) + b;
    },
    elasticIn: function (t, b, c, d, a, p) {  //正弦衰减曲线（弹动渐入）
        if (t === 0) {
            return b;
        }
        if ((t /= d) === 1) {
            return b + c;
        }
        if (!p) {
            p = d * 0.3;
        }
        let s;
        if (!a || a < Math.abs(c)) {
            a = c;
            s = p / 4;
        } else {
            s = p / (2 * Math.PI) * Math.asin(c / a);
        }
        return -(a * Math.pow(2, 10 * (t -= 1)) * Math.sin((t * d - s) * (2 * Math.PI) / p)) + b;
    },
    elasticOut: function (t, b, c, d, a, p) {    //*正弦增强曲线（弹动渐出）
        if (t === 0) {
            return b;
        }
        if ((t /= d) === 1) {
            return b + c;
        }
        if (!p) {
            p = d * 0.3;
        }
        let s;
        if (!a || a < Math.abs(c)) {
            a = c;
            s = p / 4;
        } else {
            s = p / (2 * Math.PI) * Math.asin(c / a);
        }
        return a * Math.pow(2, -10 * t) * Math.sin((t * d - s) * (2 * Math.PI) / p) + c + b;
    },
    elasticBoth: function (t, b, c, d, a, p) {
        if (t === 0) {
            return b;
        }
        if ((t /= d / 2) === 2) {
            return b + c;
        }
        if (!p) {
            p = d * (0.3 * 1.5);
        }
        let s;
        if (!a || a < Math.abs(c)) {
            a = c;
            s = p / 4;
        } else {
            s = p / (2 * Math.PI) * Math.asin(c / a);
        }
        if (t < 1) {
            return -0.5 * (a * Math.pow(2, 10 * (t -= 1)) *
                Math.sin((t * d - s) * (2 * Math.PI) / p)) + b;
        }
        return a * Math.pow(2, -10 * (t -= 1)) *
            Math.sin((t * d - s) * (2 * Math.PI) / p) * 0.5 + c + b;
    },
    backIn: function (t, b, c, d, s) {     //回退加速（回退渐入）
        if (typeof s == "undefined") {
            s = 1.70158;
        }
        return c * (t /= d) * t * ((s + 1) * t - s) + b;
    },
    backOut: function (t, b, c, d, s) {
        if (typeof s == "undefined") {
            s = 1.70158;  //回缩的距离
        }
        return c * ((t = t / d - 1) * t * ((s + 1) * t + s) + 1) + b;
    },
    backBoth: function (t, b, c, d, s) {
        if (typeof s == "undefined") {
            s = 1.70158;
        }
        if ((t /= d / 2) < 1) {
            return c / 2 * (t * t * (((s *= (1.525)) + 1) * t - s)) + b;
        }
        return c / 2 * ((t -= 2) * t * (((s *= (1.525)) + 1) * t + s) + 2) + b;
    },
    bounceIn: function (t, b, c, d) {    //弹球减振（弹球渐出）
        return c - Tween["bounceOut"](d - t, 0, c, d) + b;
    },
    bounceOut: function (t, b, c, d) {//*
        if ((t /= d) < (1 / 2.75)) {
            return c * (7.5625 * t * t) + b;
        } else if (t < (2 / 2.75)) {
            return c * (7.5625 * (t -= (1.5 / 2.75)) * t + 0.75) + b;
        } else if (t < (2.5 / 2.75)) {
            return c * (7.5625 * (t -= (2.25 / 2.75)) * t + 0.9375) + b;
        }
        return c * (7.5625 * (t -= (2.625 / 2.75)) * t + 0.984375) + b;
    },
    bounceBoth: function (t, b, c, d) {
        if (t < d / 2) {
            return Tween["bounceIn"](t * 2, 0, c, d) * 0.5 + b;
        }
        return Tween["bounceOut"](t * 2 - d, 0, c, d) * 0.5 + c * 0.5 + b;
    }
};

LsTween.transformAttr = [
    "rotate",
    "rotateX",
    "rotateY",
    "rotateZ",
    "translateX",
    "translateY",
    "translateZ",
    "scale",
    "scaleX",
    "scaleY",
    "skewX",
    "skewY"
];

LsTween.normalAttr = [
    "width",
    "height",
    "left",
    "top",
    "right",
    "bottom",
    "marginBottom",
    "marginleft",
    "marginRight",
    "marginTop",
    "paddingLeft",
    "paddingRight",
    "paddingTop",
    "paddingBottom"
];

LsTween.css = function (el, attr, val) {
    if (typeof attr == "object") {
        for (let s in attr) {
            if (attr.hasOwnProperty(s)) {
                LsTween.css(el, s, attr[s]);
            }
        }
        return;
    }
    if (LsTween.transformAttr.indexOf(attr) >= 0) {
        return LsTween.setTransform(el, attr, val);
    }
    if (val === undefined) {
        val = getComputedStyle(el)[attr];
        return LsTween.normalAttr.indexOf(attr) >= 0 || !isNaN(val) ? parseFloat(val) : val;
    } else {
        if (attr === "opacity") {
            el.style[attr] = val;
            el.style.filter = "alpha(opacity=" + (val * 100) + ")";
        } else if (LsTween.normalAttr.indexOf(attr) >= 0) {
            el.style[attr] = val + "px";
        } else if (attr === "zIndex") {
            el.style[attr] = Math.round(val).toString();
        } else {
            el.style[attr] = val;
        }
    }
};

LsTween.setTransform = function (el, attr, val) {
    el.transform = el.transform || {};
    if (val === undefined) {
        return el.transform[attr];
    }
    el.transform[attr] = val;
    let transformVal = "";
    for (let s in el.transform) {
        if (el.transform.hasOwnProperty(s)) {
            switch (s) {
                case "rotate":
                case "rotateX":
                case "rotateY":
                case "rotateZ":
                case "skewX":
                case "skewY":
                    transformVal += s + "(" + el.transform[s] + "deg) ";
                    break;
                case "translateX":
                case "translateY":
                case "translateZ":
                    transformVal += s + "(" + el.transform[s] + "px) ";
                    break;
                case "scale":
                case "scaleX":
                case "scaleY":
                    transformVal += s + "(" + el.transform[s] + ") ";
                    break;
            }
        }
    }
    el.style.WebkitTransform = el.style.transform = transformVal.trim();
};

LsTween.stop = function (el) {
    cancelAnimationFrame(el.animationTimer);
    el.animationTimer = 0;
};
