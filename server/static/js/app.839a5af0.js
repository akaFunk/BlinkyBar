(function(e){function t(t){for(var o,l,c=t[0],i=t[1],s=t[2],d=0,p=[];d<c.length;d++)l=c[d],Object.prototype.hasOwnProperty.call(n,l)&&n[l]&&p.push(n[l][0]),n[l]=0;for(o in i)Object.prototype.hasOwnProperty.call(i,o)&&(e[o]=i[o]);u&&u(t);while(p.length)p.shift()();return r.push.apply(r,s||[]),a()}function a(){for(var e,t=0;t<r.length;t++){for(var a=r[t],o=!0,c=1;c<a.length;c++){var i=a[c];0!==n[i]&&(o=!1)}o&&(r.splice(t--,1),e=l(l.s=a[0]))}return e}var o={},n={app:0},r=[];function l(t){if(o[t])return o[t].exports;var a=o[t]={i:t,l:!1,exports:{}};return e[t].call(a.exports,a,a.exports,l),a.l=!0,a.exports}l.m=e,l.c=o,l.d=function(e,t,a){l.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:a})},l.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},l.t=function(e,t){if(1&t&&(e=l(e)),8&t)return e;if(4&t&&"object"===typeof e&&e&&e.__esModule)return e;var a=Object.create(null);if(l.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)l.d(a,o,function(t){return e[t]}.bind(null,o));return a},l.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return l.d(t,"a",t),t},l.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},l.p="/";var c=window["webpackJsonp"]=window["webpackJsonp"]||[],i=c.push.bind(c);c.push=t,c=c.slice();for(var s=0;s<c.length;s++)t(c[s]);var u=i;r.push([0,"chunk-vendors"]),a()})({0:function(e,t,a){e.exports=a("56d7")},"0ae8":function(e,t,a){},1:function(e,t){},"116a":function(e,t,a){},"128f":function(e,t,a){"use strict";a("84a3")},2:function(e,t){},"4c28":function(e,t,a){"use strict";a("0ae8")},5433:function(e,t,a){"use strict";a("72b6")},"56d7":function(e,t,a){"use strict";a.r(t);a("e260"),a("e6cf"),a("cca6"),a("a79d");var o=a("7a23"),n={class:"app"},r=Object(o["createVNode"])("h1",null,"BlinkyBar Settings",-1),l={key:0},c={key:1},i=Object(o["createVNode"])("p",null,"No image uploaded.",-1),s={key:2},u=Object(o["createVNode"])("hr",null,null,-1),d=Object(o["createVNode"])("h3",null,"Debug info",-1),p=Object(o["createVNode"])("br",null,null,-1),b=Object(o["createVNode"])("br",null,null,-1),g=Object(o["createVNode"])("br",null,null,-1),m=Object(o["createVNode"])("br",null,null,-1),h=Object(o["createVNode"])("br",null,null,-1),f=Object(o["createVNode"])("br",null,null,-1),v=Object(o["createVNode"])("br",null,null,-1);function O(e,t,a,O,j,V){var y=Object(o["resolveComponent"])("slider-input"),_=Object(o["resolveComponent"])("toggle-switch"),N=Object(o["resolveComponent"])("ve-progress"),S=Object(o["resolveComponent"])("file-uploader");return Object(o["openBlock"])(),Object(o["createBlock"])("div",n,[r,Object(o["createVNode"])(y,{caption:"Speed",modelValue:e.speed,"onUpdate:modelValue":t[1]||(t[1]=function(t){return e.speed=t}),min:.1,max:10,interval:.1,unit:"m/s"},null,8,["modelValue","min","interval"]),Object(o["createVNode"])(y,{caption:"Brightness",modelValue:e.brightness,"onUpdate:modelValue":t[2]||(t[2]=function(t){return e.brightness=t}),min:1,max:100,interval:1,unit:"%","scaling-factor":100},null,8,["modelValue"]),Object(o["createVNode"])(y,{caption:"Trigger delay",modelValue:e.trigger_delay,"onUpdate:modelValue":t[3]||(t[3]=function(t){return e.trigger_delay=t}),min:0,max:60,interval:1,unit:"s"},null,8,["modelValue"]),Object(o["createVNode"])(_,{caption:"Allow scaling",modelValue:e.allow_scaling,"onUpdate:modelValue":t[4]||(t[4]=function(t){return e.allow_scaling=t})},null,8,["modelValue"]),Object(o["createVNode"])("div",null,["ready"===e.progress_status?(Object(o["openBlock"])(),Object(o["createBlock"])("div",l,[(Object(o["openBlock"])(),Object(o["createBlock"])("img",{src:e.resultUrl+e.image_hash,key:e.image_hash,alt:"scaled image stored on the BlinkyBar"},null,8,["src"]))])):Object(o["createCommentVNode"])("",!0),"noimage"===e.progress_status?(Object(o["openBlock"])(),Object(o["createBlock"])("div",c,[i])):Object(o["createCommentVNode"])("",!0),"processing"===e.progress_status||"playing"===e.progress_status?(Object(o["openBlock"])(),Object(o["createBlock"])("div",s,[Object(o["createVNode"])(N,{progress:100*e.progress_value,"empty-color":"#e1e1e1",color:"#69c0ff",size:80},{default:Object(o["withCtx"])((function(){return[Object(o["createVNode"])("legend",null,Object(o["toDisplayString"])(e.progress_percent)+" %",1)]})),_:1},8,["progress"]),Object(o["createVNode"])("p",null,Object(o["toDisplayString"])(e.progress_msg)+"...",1)])):Object(o["createCommentVNode"])("",!0)]),Object(o["createVNode"])(S,{"upload-url":"/set_image"}),u,d,Object(o["createTextVNode"])(" Speed: "+Object(o["toDisplayString"])(e.speed)+" ",1),p,Object(o["createTextVNode"])(" Brightness: "+Object(o["toDisplayString"])(e.brightness),1),b,Object(o["createTextVNode"])(" Trigger delay: "+Object(o["toDisplayString"])(e.trigger_delay),1),g,Object(o["createTextVNode"])(" Allow scaling: "+Object(o["toDisplayString"])(e.allow_scaling),1),m,Object(o["createTextVNode"])(" Progress status: "+Object(o["toDisplayString"])(e.progress_status),1),h,Object(o["createTextVNode"])(" Progress value: "+Object(o["toDisplayString"])(e.progress_value),1),f,Object(o["createTextVNode"])(" Progress msg: "+Object(o["toDisplayString"])(e.progress_msg),1),v])}a("d3b7");var j=Object(o["withScopeId"])("data-v-401765e1");Object(o["pushScopeId"])("data-v-401765e1");var V={class:"slider-container"},y={class:"slider-box"},_={class:"slider-value"};Object(o["popScopeId"])();var N=j((function(e,t,a,n,r,l){var c=Object(o["resolveComponent"])("vue-slider");return Object(o["openBlock"])(),Object(o["createBlock"])("div",null,[Object(o["createVNode"])("h3",null,Object(o["toDisplayString"])(a.caption),1),Object(o["createVNode"])("div",V,[Object(o["createVNode"])("div",y,[Object(o["createVNode"])(c,Object(o["mergeProps"])({modelValue:r.value,"onUpdate:modelValue":t[1]||(t[1]=function(e){return r.value=e}),min:a.min,max:a.max,interval:a.interval},r.slider_options,{onDragEnd:l.emitValue}),null,16,["modelValue","min","max","interval","onDragEnd"])]),Object(o["createVNode"])("div",_,[Object(o["withDirectives"])((Object(o["openBlock"])(),Object(o["createBlock"])("input",{"onUpdate:modelValue":t[2]||(t[2]=function(e){return r.value=e}),type:"number",min:a.min,max:a.max,step:a.interval,onInput:t[3]||(t[3]=function(e){return l.validateInput(e.target.value)}),key:r.inp_key,onBlur:t[4]||(t[4]=function(){return l.emitValue&&l.emitValue.apply(l,arguments)})},null,40,["min","max","step"])),[[o["vModelText"],r.value]]),Object(o["createTextVNode"])(" "+Object(o["toDisplayString"])(a.unit),1)])])])})),S=(a("a9e3"),a("4971")),k=a.n(S),w=(a("3e39"),{name:"SliderInput",components:{VueSlider:k.a},props:{name:String,caption:String,min:Number,max:Number,interval:Number,unit:String,scalingFactor:Number,modelValue:Number},emits:["update:modelValue"],data:function(){return{slider_options:{dotSize:20,width:"auto",height:10,contained:!0,direction:"ltr",data:null,dataLabel:"label",dataValue:"value",disabled:!1,clickable:!0,duration:.1,adsorb:!1,lazy:!1,tooltip:"active",tooltipPlacement:"top",tooltipFormatter:void 0,useKeyboard:!1,keydownHook:null,dragOnClick:!1,enableCross:!0,fixed:!1,minRange:void 0,maxRange:void 0,order:!0,marks:!1,dotOptions:void 0,dotAttrs:void 0,process:!0,dotStyle:void 0,railStyle:void 0,processStyle:void 0,tooltipStyle:void 0,stepStyle:void 0,stepActiveStyle:void 0,labelStyle:void 0,labelActiveStyle:void 0},value:0,factor:parseFloat(this.scalingFactor),inp_key:0}},methods:{validateInput:function(e){var t=parseFloat(e);isNaN(t)?this.inp_key+=1:t<this.min?(this.value=this.min,this.inp_key+=1):t>this.max?(this.value=this.max,this.inp_key+=1):this.value=e},emitValue:function(){console.log("Emitting new value: "+this.value),this.$emit("update:modelValue",parseFloat(this.value)/this.factor)}},watch:{modelValue:function(e){this.value=e*this.factor}},created:function(){isNaN(this.factor)&&(this.factor=1),this.value=this.modelValue*this.factor}});a("128f");w.render=N,w.__scopeId="data-v-401765e1";var x=w,B=Object(o["withScopeId"])("data-v-2df0bb69");Object(o["pushScopeId"])("data-v-2df0bb69");var D={class:"slider-value"},I={class:"switch"},U=Object(o["createVNode"])("span",{class:"slider round"},null,-1);Object(o["popScopeId"])();var C=B((function(e,t,a,n,r,l){return Object(o["openBlock"])(),Object(o["createBlock"])("div",null,[Object(o["createVNode"])("h3",null,Object(o["toDisplayString"])(a.caption),1),Object(o["createVNode"])("span",D,[Object(o["createVNode"])("label",I,[Object(o["createVNode"])("input",{type:"checkbox",checked:r.modelValue,onChange:t[1]||(t[1]=function(){return l.update&&l.update.apply(l,arguments)})},null,40,["checked"]),U]),Object(o["createTextVNode"])(" "+Object(o["toDisplayString"])(r.modelValue?"On":"Off"),1)])])})),T={name:"ToggleSwitch",props:{caption:String},data:function(){return{modelValue:Boolean}},emits:["update:modelValue"],methods:{update:function(e){this.modelValue=e.target.checked,this.$emit("update:modelValue",this.modelValue)}}};a("5433");T.render=C,T.__scopeId="data-v-2df0bb69";var P=T,F=Object(o["withScopeId"])("data-v-0c147faf");Object(o["pushScopeId"])("data-v-0c147faf");var A={class:"file-uploader-box"};Object(o["popScopeId"])();var M=F((function(e,t,a,n,r,l){return Object(o["openBlock"])(),Object(o["createBlock"])("div",A,[Object(o["createVNode"])("input",{type:"file",style:{display:"none"},ref:"file",accept:"image/*",onChange:t[1]||(t[1]=function(){return l.onFileChange&&l.onFileChange.apply(l,arguments)})},null,544),Object(o["createVNode"])("button",{class:"upload-btn",onClick:t[2]||(t[2]=function(t){return e.$refs.file.click()})},"Upload new image")])})),z=(a("b0c0"),{name:"FileUploader",components:{},props:["uploadUrl"],data:function(){return{}},methods:{onFileChange:function(e){console.log(e.target.files[0].name);var t=e.target.files[0],a=new FormData;a.append("image_obj",t),fetch(this.uploadUrl,{method:"PUT",body:a})}}});a("5d95");z.render=M,z.__scopeId="data-v-0c147faf";var E=z,$=a("6bf9"),J=a("1ad9"),R={name:"App",components:{SliderInput:x,ToggleSwitch:P,FileUploader:E,VeProgress:$["VeProgress"]},data:function(){return{resultUrl:"/get_image_scaled?fake_param=",settingsUrl:"/settings",speed:0,brightness:0,trigger_delay:0,allow_scaling:!0,image_hash:"",progress_status:"",progress_value:0,progress_percent:0,progress_msg:"",timer:setInterval(this.fetchData,200)}},methods:{fetchData:function(){var e=this;fetch(this.settingsUrl).then((function(e){return e.json()})).then((function(t){return e.processNewData(t)}))},processNewData:function(e){this.speed=e.speed,this.brightness=e.brightness,this.trigger_delay=e.trigger_delay,this.allow_scaling=e.allow_scaling,this.image_hash=e.image_hash,this.progress_status=e.progress_status,this.progress_value=e.progress_value,this.progress_msg=e.progress_msg,this.progress_percent=J("%.1f",100*this.progress_value)},update:function(e,t){console.log(this.settingsUrl+"?"+e+"="+t),fetch(this.settingsUrl+"?"+e+"="+t)}},watch:{speed:function(e){this.update("speed",e)},brightness:function(e){this.update("brightness",e)},trigger_delay:function(e){this.update("trigger_delay",e)},allow_scaling:function(e){this.update("allow_scaling",e)}},created:function(){this.fetchData()}};a("4c28");R.render=O;var H=R;Object(o["createApp"])(H).mount("#app")},"5d95":function(e,t,a){"use strict";a("116a")},"72b6":function(e,t,a){},"84a3":function(e,t,a){}});
//# sourceMappingURL=app.839a5af0.js.map