define((function(){return function(e){var t={};function r(n){if(t[n])return t[n].exports;var i=t[n]={i:n,l:!1,exports:{}};return e[n].call(i.exports,i,i.exports,r),i.l=!0,i.exports}return r.m=e,r.c=t,r.d=function(e,t,n){r.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},r.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},r.t=function(e,t){if(1&t&&(e=r(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(r.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var i in e)r.d(n,i,function(t){return e[t]}.bind(null,i));return n},r.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return r.d(t,"a",t),t},r.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},r.p="",r(r.s=1)}([function(e,t,r){"use strict";function n(e){return(n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function i(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t){return!t||"object"!==n(t)&&"function"!=typeof t?o(e):t}function o(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function u(e){var t="function"==typeof Map?new Map:void 0;return(u=function(e){if(null===e||(r=e,-1===Function.toString.call(r).indexOf("[native code]")))return e;var r;if("function"!=typeof e)throw new TypeError("Super expression must either be null or a function");if(void 0!==t){if(t.has(e))return t.get(e);t.set(e,n)}function n(){return s(e,arguments,p(this).constructor)}return n.prototype=Object.create(e.prototype,{constructor:{value:n,enumerable:!1,writable:!0,configurable:!0}}),f(n,e)})(e)}function s(e,t,r){return(s=c()?Reflect.construct:function(e,t,r){var n=[null];n.push.apply(n,t);var i=new(Function.bind.apply(e,n));return r&&f(i,r.prototype),i}).apply(null,arguments)}function c(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Date.prototype.toString.call(Reflect.construct(Date,[],(function(){}))),!0}catch(e){return!1}}function f(e,t){return(f=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function p(e){return(p=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}Object.defineProperty(t,"__esModule",{value:!0});var l=function(e){!function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&f(e,t)}(h,e);var t,r,n,u,s,l=(t=h,r=c(),function(){var e,n=p(t);if(r){var i=p(this).constructor;e=Reflect.construct(n,arguments,i)}else e=n.apply(this,arguments);return a(this,e)});function h(e){var t;return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,h),(t=l.call(this,"Aggregated Exceptions: \n  "+e.map((function(e){return h.makeNice(e)})).join("\n"))).errors=e,Object.setPrototypeOf(o(t),(this instanceof h?this.constructor:void 0).prototype),t}return n=h,s=[{key:"makeNice",value:function(e){return e instanceof Error?"  ".concat(e.name,": ").concat(e.message,"\n    ").concat(e.stack.split("\n").map((function(e){return"    "+e})).join("\n")):"  "+e.toString()}}],(u=null)&&i(n.prototype,u),s&&i(n,s),h}(u(Error));t.AggregateError=l,t.k2a=function(e){if("function"==typeof e.keys)return Array.from(e.keys());var t=[];return e.forEach((function(e,r){return t.push(r)})),t},t.v2a=function(e){if("function"==typeof e.keys)return Array.from(e.values());var t=[];return e.forEach((function(e){return t.push(e)})),t}},function(e,t,r){"use strict";r.r(t),r.d(t,"load_ipython_extension",(function(){return n}));r(2);function n(){console.log("Loading Yuuno2 for Jupyter Notebook")}},function(e,t,r){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=r(3);t.LocalClip=n.LocalClip,t.RemoteClip=n.RemoteClip},function(e,t,r){"use strict";function n(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t,r){return t&&i(e.prototype,t),r&&i(e,r),e}var o=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0});var u=r(4),s=r(10),c=function(){function e(t){n(this,e),this.clip=t}return a(e,[{key:"with_frame",value:function(e,t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){var n,i,a,u,c=this;return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:if(n=this,i=e.text.size||null,a=this.clip,null===i){r.next=10;break}return r.next=6,this.clip.resize(i);case 6:if(r.t0=r.sent,r.t0){r.next=9;break}r.t0=a;case 9:a=r.t0;case 10:return u=e.text.frameno,r.t1=s,r.next=14,a.get(u);case 14:return r.t2=r.sent,r.t3=function(e){return o(c,void 0,void 0,regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,t.apply(n,e);case 2:return r.abrupt("return",r.sent);case 3:case"end":return r.stop()}}),r)})))},r.next=18,r.t1.using.call(r.t1,r.t2,r.t3);case 18:return r.abrupt("return",r.sent);case 19:case"end":return r.stop()}}),r,this)})))}},{key:"on_length",value:function(e){return{text:{length:this.clip.size},blobs:[]}}},{key:"on_format",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this.with_frame(e,(function(e){return o(n,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.nativeFormat();case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t)})))}));case 2:return r=t.sent,t.abrupt("return",{text:{format:r.toJSON()},blobs:[]});case 4:case"end":return t.stop()}}),t,this)})))}},{key:"on_size",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this.with_frame(e,(function(e){return o(n,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.size();case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t)})))}));case 2:return r=t.sent,t.abrupt("return",{text:r,blobs:[]});case 4:case"end":return t.stop()}}),t,this)})))}},{key:"on_metadata",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if("number"==typeof e.text.frameno){t.next=6;break}return t.next=3,this.clip.metadata();case 3:r=t.sent,t.next=9;break;case 6:return t.next=8,this.with_frame(e,(function(e){return o(n,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.metadata();case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t)})))}));case 8:r=t.sent;case 9:return t.abrupt("return",{text:{metadata:s.toObject(r)},blobs:[]});case 10:case"end":return t.stop()}}),t,this)})))}},{key:"on_can_render",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n,i=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return r=u.RawFormat.fromJSON(e.text.format),t.next=3,this.with_frame(e,(function(e){return o(i,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.canRender(r);case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t)})))}));case 3:return n=t.sent,t.abrupt("return",{text:{supported:n},blobs:[]});case 5:case"end":return t.stop()}}),t,this)})))}},{key:"on_render",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n,i,a,s=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return r=u.RawFormat.fromJSON(e.text.format),n=e.text.planes,i=n instanceof Array?n:[n],t.next=5,this.with_frame(e,(function(e){return o(s,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(e.canRender(r)){t.next=2;break}return t.abrupt("return",null);case 2:return t.next=4,e.render(i,r);case 4:return t.abrupt("return",t.sent);case 5:case"end":return t.stop()}}),t)})))}));case 5:if(null!==(a=t.sent)){t.next=10;break}return t.abrupt("return",{text:{success:!1},blobs:[]});case 10:return t.abrupt("return",{text:{success:!0},blobs:a});case 11:case"end":return t.stop()}}),t,this)})))}}]),e}();t.LocalClip=c;var f=function(e){e.registerType("yuuno2:clip","length","format","size","metadata","can_render","render")};function p(e){var t=e.close,r=0;return e.close=function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){for(;;)switch(n.prev=n.next){case 0:(r-=1)<=0&&t.apply(e);case 2:case"end":return n.stop()}}),n)})))},e.open=function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:r+=1;case 1:case"end":return e.stop()}}),e)})))},e}var l=function(){function e(t,r,i){n(this,e),this.proxy=t,this.frameno=r,this._desiredSize=i}return a(e,[{key:"nativeFormat",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.t0=u.RawFormat,e.next=3,this.proxy.format({text:{frameno:this.frameno},blobs:[]});case 3:return e.t1=e.sent.text,e.abrupt("return",e.t0.fromJSON.call(e.t0,e.t1));case 5:case"end":return e.stop()}}),e,this)})))}},{key:"size",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(null===this._desiredSize){e.next=2;break}return e.abrupt("return",this._desiredSize);case 2:return e.next=4,this.proxy.size({text:{frameno:this.frameno},blobs:[]});case 4:return e.abrupt("return",e.sent.text);case 5:case"end":return e.stop()}}),e,this)})))}},{key:"metadata",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.t0=s,e.next=3,this.proxy.metadata({text:{frameno:this.frameno},blobs:[]});case 3:return e.t1=e.sent.text.metadata,e.abrupt("return",e.t0.object2map.call(e.t0,e.t1));case 5:case"end":return e.stop()}}),e,this)})))}},{key:"canRender",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this.proxy.can_render({text:{frameno:this.frameno,format:e.toJSON(),size:this._desiredSize},blobs:[]});case 2:return r=t.sent,t.abrupt("return",r.text.supported);case 4:case"end":return t.stop()}}),t,this)})))}},{key:"render",value:function(e,t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){var n,i;return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return(n=e instanceof Array)||(e=[e]),r.next=4,this.proxy.render({text:{frameno:this.frameno,planes:e,format:t.toJSON(),size:this._desiredSize},blobs:[]});case 4:if((i=r.sent).text.success){r.next=7;break}throw new Error("Failed to render video.");case 7:if(!n){r.next=11;break}return r.abrupt("return",i.blobs[0]);case 11:return r.abrupt("return",i.blobs);case 12:case"end":return r.stop()}}),r,this)})))}},{key:"open",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this.proxy.open();case 2:case"end":return e.stop()}}),e,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this.proxy.close();case 2:case"end":return e.stop()}}),e,this)})))}}]),e}();t.RemoteFrame=l;var h=function(){function e(t,r){var i=arguments.length>2&&void 0!==arguments[2]?arguments[2]:null;n(this,e),this.proxy=t,this._desiredSize=i,this._length=r}return a(e,[{key:"metadata",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.t0=s,e.next=3,this.proxy.metadata({text:{frameno:null},blobs:[]});case 3:return e.t1=e.sent.text.metadata,e.abrupt("return",e.t0.object2map.call(e.t0,e.t1));case 5:case"end":return e.stop()}}),e,this)})))}},{key:"get",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return r=new l(this.proxy,e,this._desiredSize),t.next=3,r.open();case 3:return t.abrupt("return",r);case 4:case"end":return t.stop()}}),t,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this.proxy.close();case 2:case"end":return e.stop()}}),e,this)})))}},{key:"resize",value:function(t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.proxy.open();case 2:return r.abrupt("return",new e(this.proxy,this._length,t));case 3:case"end":return r.stop()}}),r,this)})))}},{key:"size",get:function(){return this._length}}],[{key:"from_proxy",value:function(t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){var n,i;return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return n=p(t),r.next=3,n.open();case 3:return r.next=5,n.length({text:{},blobs:[]});case 5:return i=r.sent.text.length,r.abrupt("return",new e(n,i));case 7:case"end":return r.stop()}}),r)})))}},{key:"from_rpc",value:function(t,r){return o(this,void 0,void 0,regeneratorRuntime.mark((function n(){var i;return regeneratorRuntime.wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return f(r),i=r.get(t,"yuuno2:clip"),n.next=4,e.from_proxy(i);case 4:return n.abrupt("return",n.sent);case 5:case"end":return n.stop()}}),n)})))}},{key:"from_manager",value:function(t,r,n){return o(this,void 0,void 0,regeneratorRuntime.mark((function i(){var a;return regeneratorRuntime.wrap((function(i){for(;;)switch(i.prev=i.next){case 0:return f(r),i.next=3,n.get(t,"yuuno2:clip");case 3:return a=i.sent,i.next=6,e.from_proxy(a);case 6:return i.abrupt("return",i.sent);case 7:case"end":return i.stop()}}),i)})))}}]),e}();t.RemoteClip=h},function(e,t,r){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=r(5);t.RawFormat=n.RawFormat,t.SampleType=n.SampleType,t.ColorFamily=n.ColorFamily,function(e){var t;t=r(6),e.Clip=t.SimpleClip,e.Frame=t.SimpleFrame,e.Script=r(7).SimpleScript}(t.Simple||(t.Simple={}));var i=r(8);t.SingleScriptProvider=i.SingleScriptProvider;var a=r(9);t.NamedScriptProvider=a.NamedScriptProvider;var o=r(0);t.AggregateError=o.AggregateError},function(e,t,r){"use strict";function n(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t,r){return t&&i(e.prototype,t),r&&i(e,r),e}var o;Object.defineProperty(t,"__esModule",{value:!0}),function(e){e[e.INTEGER=0]="INTEGER",e[e.FLOAT=1]="FLOAT"}(o=t.SampleType||(t.SampleType={}));var u=function(){function e(t,r,i,a){n(this,e),this._v1num=t,this._planes=r,this._name=i,this._fields=a}return a(e,[{key:"v1num",get:function(){return this._v1num}},{key:"planes",get:function(){return this._planes}},{key:"name",get:function(){return this._name}},{key:"fields",get:function(){return Array.from(this._fields)}}],[{key:"getColorFamilyByName",value:function(t){switch(t){case"grey":case"gray":return e.GREY;case"rgb":return e.RGB;case"yuv":return e.YUV;case"cmyk":return e.CMYK;default:return null}}}]),e}();t.ColorFamily=u,u.GREY=new u(0,1,"grey",["y"]),u.RGB=new u(1,3,"rgb",["r","g","b"]),u.YUV=new u(2,3,"yuv",["y","u","v"]),u.CMYK=new u(3,4,"cmyk",["c","m","y","k"]);var s=function(){function e(t,r,i,a,o,u,s,c){n(this,e),this._bitsPerSample=t,this._isPlanar=o,this._hasAlpha=u,this._colorFamily=s,this._sampleType=c,this._subsampling=a,this._alignment=i,this._fieldOrder=r}return a(e,[{key:"toJSON",value:function(){return[{type:"video",colorspace:{family:this._colorFamily.name,alpha:this._hasAlpha,fields:this._fieldOrder},dataformat:{type:this._sampleType==o.FLOAT?"float":"integer",size:this._bitsPerSample},planar:this._isPlanar,subsampling:this._subsampling,alignment:this._alignment},"v2"]}},{key:"getPlaneDimensions",value:function(e,t){if(!this._isPlanar)return t;var r=t.width,n=t.height;return 0<e&&e<4&&(r>>=this._subsampling[0],n>>=this._subsampling[1]),{width:r,height:n}}},{key:"getStride",value:function(e,t){var r=this.getPlaneDimensions(e,t).width*this.bytesPerSample;this._isPlanar||(r*=this._fieldOrder.length);var n=this.alignment;return r%n!=0&&(r+=n-r%n),r}},{key:"getPlaneSize",value:function(e,t){var r=this.getStride(e,t);return t.height*r}},{key:"bitsPerSample",get:function(){return this._bitsPerSample}},{key:"bytesPerSample",get:function(){return Math.floor((this._bitsPerSample+7)/8)}},{key:"numFields",get:function(){return this._colorFamily.fields.length+(this._hasAlpha?1:0)}},{key:"numPlanes",get:function(){return this._isPlanar?this.numFields:1}},{key:"alignment",get:function(){return 0==this._alignment?this._isPlanar?this.bytesPerSample:this.bytesPerSample*this.numFields:this._alignment}}],[{key:"fromJSON",value:function(t){var r=t[t.length-1];if("v1"==r){var n=[u.GREY,u.RGB,u.YUV][t[2]],i=[o.INTEGER,o.FLOAT][t[3]],a=t[0],s=t[6]?4:Math.floor((a+7)/8),c=n.planes+1==t[1],f=n.fields;c?f.push("a"):t[6]&&f.push(null),t=[{type:"video",colorspace:{family:n.name,alpha:c,fields:f},dataformat:{type:i==o.FLOAT?"float":"integer",size:a},planar:t[7],subsampling:[t[5],t[4]],alignment:s},"v2"]}if("v2"==r){var p,l=t[0];switch(l.colorspace.family){case"grey":p=u.GREY;break;case"yuv":p=u.RGB;break;case"rgb":p=u.YUV;break;default:return null}var h=l.colorspace.fields,m=l.colorspace.hasAlpha,v="integer"==l.dataformat.type?o.INTEGER:o.FLOAT,d=l.dataformat.size,g=l.dataformat.planar,y=l.dataformat.subsampling;return new e(d,h,l.dataformat.alignment,y,g,m,p,v)}return null}},{key:"simple",value:function(t,r,n,i){var a=t.fields;return r&&a.push("a"),new e(i,a,0,[0,0],!0,r,t,n)}}]),e}();t.RawFormat=s,s.RGBA32=new s(8,["r","g","b","a"],4,[0,0],!1,!0,u.RGB,o.INTEGER),s.RGBX32=new s(8,["r","g","b",null],4,[0,0],!1,!1,u.RGB,o.INTEGER),s.RGB24=new s(8,["r","g","b"],1,[0,0],!0,!1,u.RGB,o.INTEGER),s.GREY8=new s(8,["y"],1,[0,0],!0,!1,u.GREY,o.INTEGER)},function(e,t,r){"use strict";function n(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t,r){return t&&i(e.prototype,t),r&&i(e,r),e}var o=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0});var u=function(){function e(t,r,i,a){n(this,e),this.__closed=!1,this._nativeFormat=t,this._size=r,this._metadata=i,this._planes=a}return a(e,[{key:"ensureOpen",value:function(){if(this.__closed)throw new Error("Frame is closed")}},{key:"nativeFormat",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return this.ensureOpen(),e.abrupt("return",this._nativeFormat);case 2:case"end":return e.stop()}}),e,this)})))}},{key:"size",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return this.ensureOpen(),e.abrupt("return",this._size);case 2:case"end":return e.stop()}}),e,this)})))}},{key:"metadata",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return this.ensureOpen(),e.abrupt("return",this._metadata);case 2:case"end":return e.stop()}}),e,this)})))}},{key:"canRender",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return this.ensureOpen(),t.abrupt("return",e===this._nativeFormat);case 2:case"end":return t.stop()}}),t,this)})))}},{key:"render",value:function(e,t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){var n=this;return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:if(this.ensureOpen(),!(e instanceof Array)){r.next=5;break}return r.next=4,Promise.all(e.map((function(e){return o(n,void 0,void 0,regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.render(e,t);case 2:return r.abrupt("return",r.sent);case 3:case"end":return r.stop()}}),r,this)})))})));case 4:return r.abrupt("return",r.sent);case 5:return r.abrupt("return",this._planes[e]);case 6:case"end":return r.stop()}}),r,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:this.__closed=!0;case 1:case"end":return e.stop()}}),e,this)})))}}]),e}();t.SimpleFrame=u;var s=function(){function e(t,r,i,a){n(this,e),this._frames=t,this._metadata=r,this._format=i,this._size=a}return a(e,[{key:"metadata",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.abrupt("return",this._metadata);case 1:case"end":return e.stop()}}),e,this)})))}},{key:"get",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",new u(this._format,this._size,this._metadata,this._frames[e]));case 1:case"end":return t.stop()}}),t,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:case"end":return e.stop()}}),e)})))}},{key:"resize",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.abrupt("return",null);case 1:case"end":return e.stop()}}),e)})))}},{key:"size",get:function(){return this._frames.length}}]),e}();t.SimpleClip=s},function(module,exports,__webpack_require__){"use strict";function _classCallCheck(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function _defineProperties(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function _createClass(e,t,r){return t&&_defineProperties(e.prototype,t),r&&_defineProperties(e,r),e}var __awaiter=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(exports,"__esModule",{value:!0});var utils_1=__webpack_require__(0),SimpleScript=function(){function SimpleScript(){_classCallCheck(this,SimpleScript),this.config=new Map,this.ctx={},this.clips=new Map;var e=this;this.ctx.register=function(t,r){return e.clips.set(t,r)}}return _createClass(SimpleScript,[{key:"setConfig",value:function(e,t){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:this.config.set(e,t);case 1:case"end":return r.stop()}}),r,this)})))}},{key:"getConfig",value:function(e){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",this.config.get(e));case 1:case"end":return t.stop()}}),t,this)})))}},{key:"listConfig",value:function(){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.abrupt("return",utils_1.k2a(this.config));case 1:case"end":return e.stop()}}),e,this)})))}},{key:"run",value:function run(code){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function _callee4(){return regeneratorRuntime.wrap((function _callee4$(_context4){for(;;)switch(_context4.prev=_context4.next){case 0:code instanceof ArrayBuffer&&(code=String.fromCharCode.apply(null,new Uint16Array(code))),function(){eval(code)}.call(this.ctx);case 2:case"end":return _context4.stop()}}),_callee4,this)})))}},{key:"listClips",value:function(){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.abrupt("return",utils_1.k2a(this.clips));case 1:case"end":return e.stop()}}),e,this)})))}},{key:"getClip",value:function(e){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",this.clips.get(e));case 1:case"end":return t.stop()}}),t,this)})))}},{key:"close",value:function(){return __awaiter(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:this.ctx=null,this.clips=null;case 2:case"end":return e.stop()}}),e,this)})))}}]),SimpleScript}();exports.SimpleScript=SimpleScript},function(e,t,r){"use strict";function n(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}var i=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0});var a=function(){function e(t){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this._script=t}var t,r,a;return t=e,(r=[{key:"get",value:function(e){return i(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.abrupt("return",this._script);case 1:case"end":return e.stop()}}),e,this)})))}},{key:"close",value:function(){return i(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this._script.close();case 2:case"end":return e.stop()}}),e,this)})))}}])&&n(t.prototype,r),a&&n(t,a),e}();t.SingleScriptProvider=a},function(e,t,r){"use strict";function n(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var r=0;r<t.length;r++){var n=t[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function a(e,t,r){return t&&i(e.prototype,t),r&&i(e,r),e}var o=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0});var u=r(0),s=function(){function e(t,r){n(this,e),this._parent=t,this._onClose=r}return a(e,[{key:"setConfig",value:function(e,t){return o(this,void 0,void 0,regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this._parent.setConfig(e,t);case 2:case"end":return r.stop()}}),r,this)})))}},{key:"getConfig",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this._parent.getConfig(e);case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t,this)})))}},{key:"listConfig",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this._parent.listConfig();case 2:return e.abrupt("return",e.sent);case 3:case"end":return e.stop()}}),e,this)})))}},{key:"run",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this._parent.run(e);case 2:case"end":return t.stop()}}),t,this)})))}},{key:"listClips",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this._parent.listClips();case 2:return e.abrupt("return",e.sent);case 3:case"end":return e.stop()}}),e,this)})))}},{key:"getClip",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this._parent.getClip(e);case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,this._parent.close();case 3:return e.prev=3,this._onClose(),e.finish(3);case 6:case"end":return e.stop()}}),e,this,[[0,,3,6]])})))}}]),e}(),c=function(){function e(t){var r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"name";n(this,e),this._cache=new Map,this._parent=t,this._optionName=r}return a(e,[{key:"get",value:function(e){return o(this,void 0,void 0,regeneratorRuntime.mark((function t(){var r,n,i=this;return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(void 0!==e[this._optionName]){t.next=4;break}return t.next=3,this._parent.get(e);case 3:return t.abrupt("return",t.sent);case 4:if(r=e[this._optionName],delete e[this._optionName],!this._cache.has(r)){t.next=8;break}return t.abrupt("return",this._cache.get(r));case 8:return t.t0=s,t.next=11,this._parent.get(e);case 11:return t.t1=t.sent,t.t2=function(){return i._cache.delete(r)},n=new t.t0(t.t1,t.t2),this._cache.set(r,n),t.abrupt("return",n);case 16:case"end":return t.stop()}}),t,this)})))}},{key:"close",value:function(){return o(this,void 0,void 0,regeneratorRuntime.mark((function e(){var t,r,n=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=[],r=[],u.v2a(this._cache).map((function(e){return o(n,void 0,void 0,regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,e.close().then((function(e){return e}),(function(e){return r.push(e)}));case 2:return t.abrupt("return",t.sent);case 3:case"end":return t.stop()}}),t)})))})),e.next=5,Promise.all(t);case 5:if(!(r.length>0)){e.next=7;break}throw new u.AggregateError(r);case 7:return e.next=9,this._parent.close();case 9:case"end":return e.stop()}}),e,this)})))}}]),e}();t.NamedScriptProvider=c},function(e,t,r){"use strict";var n=this&&this.__awaiter||function(e,t,r,n){return new(r||(r=Promise))((function(i,a){function o(e){try{s(n.next(e))}catch(e){a(e)}}function u(e){try{s(n.throw(e))}catch(e){a(e)}}function s(e){var t;e.done?i(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t)}))).then(o,u)}s((n=n.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0}),t.using=function(e,t){return n(this,void 0,void 0,regeneratorRuntime.mark((function r(){var n;return regeneratorRuntime.wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.prev=0,r.next=3,t(e);case 3:n=r.sent;case 4:return r.prev=4,r.next=7,e.close();case 7:return r.finish(4);case 8:return r.abrupt("return",n);case 9:case"end":return r.stop()}}),r,null,[[0,,4,8]])})))},t.toObject=function(e){var t={};return e.forEach((function(e,r){return t[r]=e})),t},t.object2map=function(e){for(var t=new Map,r=0,n=Object.keys(e);r<n.length;r++){var i=n[r];t.set(i,e[i])}return t}}])}));
//# sourceMappingURL=yuuno2notebook.js.map