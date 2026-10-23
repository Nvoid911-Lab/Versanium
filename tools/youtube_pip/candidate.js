(() => {
  'use strict';
  if (window.top !== window || location.protocol !== 'https:' ||
      !['youtube.com','www.youtube.com','m.youtube.com'].includes(location.hostname)) return null;
  const options = __VERSANIUM_OPTIONS__;
  let state = window.__versaniumYoutubeState;
  if (state && (typeof state.adjust !== 'function' || typeof state.mobile !== 'boolean')) return null;
  if (!state && !Object.isExtensible(window)) return null;
  if (!state) {
    state = {mobile:false,pip:false,background:false,pauses:0,visibilityEvents:0,pipAdjusted:false,backgroundInstalled:false};
    Object.defineProperty(window,'__versaniumYoutubeState',{value:state});
    const nativeHidden = Object.getOwnPropertyDescriptor(Document.prototype,'hidden');
    const nativeVisibility = Object.getOwnPropertyDescriptor(Document.prototype,'visibilityState');
    // Unknown DOM/descriptor: safely leave background behavior unchanged.
    if (nativeHidden && nativeVisibility && typeof nativeHidden.get === 'function' &&
        typeof nativeVisibility.get === 'function' &&
        Object.isExtensible(document) && !Object.getOwnPropertyDescriptor(document,'hidden') &&
        !Object.getOwnPropertyDescriptor(document,'visibilityState')) {
      Object.defineProperty(document,'hidden',{configurable:true,get(){
        return state.mobile && state.background ? false : nativeHidden.get.call(this);
      }});
      Object.defineProperty(document,'visibilityState',{configurable:true,get(){
        return state.mobile && state.background ? 'visible' : nativeVisibility.get.call(this);
      }});
      state.backgroundInstalled = true;
      document.addEventListener('visibilitychange', event => {
        state.visibilityEvents++;
        if (state.mobile && state.background) event.stopImmediatePropagation();
      },true);
    }
    const adjust = () => {
      if (!state.mobile || !state.pip) return;
      for (const video of document.querySelectorAll('video')) {
        if ('disablePictureInPicture' in video && video.disablePictureInPicture === true) {
          video.disablePictureInPicture = false;
          video.removeAttribute('disablepictureinpicture');
          state.pipAdjusted = true;
        }
      }
    };
    if (typeof MutationObserver === 'function') {
      new MutationObserver(adjust).observe(document,{subtree:true,childList:true,
        attributes:true,attributeFilter:['disablepictureinpicture']});
    }
    document.addEventListener('pause',event => {
      if (event.target instanceof HTMLVideoElement) state.pauses++;
    },true);
    state.adjust = adjust;
  }
  state.mobile = options.mobile;
  state.pip = options.pip;
  state.background = options.background;
  state.adjust();
  // Fixed booleans/counts only; no URL/title/config/video ID or page-provided strings.
  return {mobile:!!state.mobile,pip:!!state.pip,background:!!state.background,
    pipAdjusted:!!state.pipAdjusted,backgroundApplied:!!(state.mobile && state.background && state.backgroundInstalled),pauseObserved:state.pauses>0,
    visibilityObserved:state.visibilityEvents>0,
    paused:!!document.querySelector('video')?.paused};
})()
