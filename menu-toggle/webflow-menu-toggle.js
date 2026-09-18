/* shanny.design menu toggle: click opens .menu_open and plays the Lottie 0->30; click again reverses. */
(function(){var T='.toggle_wrap',M='.menu_open',F=260,n=0,t=setInterval(s,120);s();
function s(){var d=false;try{d=b()}catch(e){}if(d||++n>80){clearInterval(t)}}
function b(){var w=document.querySelector(T),m=document.querySelector(M);if(!w||!m){return false}
if(w.getAttribute('data-menu-bound')){return true}var a=lot(w);
if(a){a.loop=false;a.autoplay=false;a.goToAndStop(0,true)}
w.setAttribute('data-menu-bound','1');w.style.cursor='pointer';
m.style.transition='opacity '+F+'ms ease';
var o=false,q=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function set(x){if(x===o){return}o=x;
if(o){m.style.display='flex';m.style.opacity='0';void m.offsetHeight;m.style.opacity='1'}
else{m.style.opacity='0';setTimeout(function(){if(!o){m.style.display='none'}},q?0:F)}
if(a){try{if(q){a.goToAndStop(o?a.totalFrames-1:0,true)}else{a.setDirection(o?1:-1);a.play()}}catch(e){}}}
w.addEventListener('click',function(){set(!o)});
m.addEventListener('click',function(e){if(e.target&&e.target.closest&&e.target.closest('a')){set(false)}});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&o){set(false)}});return true}
function lot(w){try{var r=window.Webflow&&window.Webflow.require&&window.Webflow.require('lottie'),
p=r&&r.lottie;if(!p||typeof p.getRegisteredAnimations!=='function'){return null}
var l=p.getRegisteredAnimations()||[];for(var i=0;i<l.length;i++){
if(l[i]&&l[i].wrapper&&w.contains(l[i].wrapper)&&l[i].isLoaded){return l[i]}}}catch(e){}return null}})();
