(() => {
  'use strict';
  if (window.top !== window || location.protocol !== 'https:' ||
      !['youtube.com','www.youtube.com','m.youtube.com'].includes(location.hostname)) return null;
  const options = __VERSANIUM_OPTIONS__;
  const isPlaying = () => {
    const video = document.querySelector('video');
    return !!video && !video.paused && !video.ended;
  };
  let state = window.__versaniumYoutubeState;
  if (state && (typeof state.adjust !== 'function' || typeof state.mobile !== 'boolean')) return null;
  if (!state && !Object.isExtensible(window)) return null;
  if (!state) {
    state = {mobile:false,pip:false,background:false,pauses:0,pauseMethodObserved:false,pauseWithActivation:false,visibilityEvents:0,pipAdjusted:false,backgroundInstalled:false};
    Object.defineProperty(window,'__versaniumYoutubeState',{value:state});
    const nativeHidden = Object.getOwnPropertyDescriptor(Document.prototype,'hidden');
    const nativeVisibility = Object.getOwnPropertyDescriptor(Document.prototype,'visibilityState');
    // Unknown DOM/descriptor: safely leave background behavior unchanged.
    if (options.background && nativeHidden && nativeVisibility && typeof nativeHidden.get === 'function' &&
        typeof nativeVisibility.get === 'function' &&
        Object.isExtensible(document) && !Object.getOwnPropertyDescriptor(document,'hidden') &&
        !Object.getOwnPropertyDescriptor(document,'visibilityState')) {
      Object.defineProperty(document,'hidden',{configurable:true,get(){
        return state.mobile && state.background && isPlaying() ? false : nativeHidden.get.call(this);
      }});
      Object.defineProperty(document,'visibilityState',{configurable:true,get(){
        return state.mobile && state.background && isPlaying() ? 'visible' : nativeVisibility.get.call(this);
      }});
      state.backgroundInstalled = true;
      document.addEventListener('visibilitychange', event => {
        state.visibilityEvents++;
        if (state.mobile && state.background && isPlaying()) event.stopImmediatePropagation();
      },true);
    }
    const attempts = new WeakMap();
    const watched = new WeakSet();
    // Ownership ends on ANY observed site attribute mutation, including true->false.
    // A comparison of the final boolean alone would lose those intervening writes.
    const owned = new Map();
    let observer;
    const reconcile = records => {
      for (const record of records) {
        if (record.type === 'attributes' && record.attributeName === 'disablepictureinpicture') {
          owned.delete(record.target);
        }
      }
    };
    const drainExternal = () => { if (observer) reconcile(observer.takeRecords()); };
    const ownWrite = (video, write) => {
      drainExternal();
      write();
      // Drop only our own reflected attribute records; retain other targets' site changes.
      if (observer) reconcile(observer.takeRecords().filter(record =>
        record.target !== video || record.type !== 'attributes' ||
        record.attributeName !== 'disablepictureinpicture'));
    };
    const adjust = () => {
      drainExternal();
      if (!state.mobile || !state.pip) {
        for (const [video, original] of owned) {
          if (video.isConnected && !Object.getOwnPropertyDescriptor(video,'disablePictureInPicture') && video.disablePictureInPicture === false &&
              !video.hasAttribute('disablepictureinpicture')) {
            ownWrite(video, () => video.setAttribute('disablepictureinpicture',original));
          }
        }
        owned.clear();
        if (!state.mobile) return;
      }
      for (const video of owned.keys()) { if (!video.isConnected) owned.delete(video); }
      for (const video of document.querySelectorAll('video')) {
        if (state.diagnostics && !watched.has(video) && typeof video.pause === 'function' &&
            Object.isExtensible(video) && !Object.getOwnPropertyDescriptor(video,'pause')) {
          watched.add(video);
          const pause = video.pause;
          video.pause = function(...args) {
            if (state.mobile && state.diagnostics) {
              state.pauseMethodObserved = true;
              state.pauseWithActivation = !!navigator.userActivation?.isActive;
            }
            return Reflect.apply(pause,this,args);
          };
        }
        if (state.pip && observer && !video.paused && !video.ended && !Object.getOwnPropertyDescriptor(video,'disablePictureInPicture') && 'disablePictureInPicture' in video && video.disablePictureInPicture === true && (attempts.get(video) || 0) < 8) {
          attempts.set(video,(attempts.get(video) || 0)+1);
          // The standardized reflected boolean must match the DOM attribute contract.
          if (!video.hasAttribute('disablepictureinpicture')) continue;
          const original = video.getAttribute('disablepictureinpicture');
          ownWrite(video, () => { video.disablePictureInPicture = false; });
          if (video.disablePictureInPicture !== false || video.hasAttribute('disablepictureinpicture')) continue;
          owned.set(video,original);
          state.pipAdjusted = true;
        }
      }
    };
    if (typeof MutationObserver === 'function') {
      observer = new MutationObserver(records => { reconcile(records);adjust(); });
      observer.observe(document,{subtree:true,childList:true,
        attributes:true,attributeFilter:['disablepictureinpicture']});
    }
    document.addEventListener('play',adjust,true);
    document.addEventListener('pause',event => {
      if (event.target instanceof HTMLVideoElement) state.pauses++;
    },true);
    state.adjust = adjust;
  }
  state.mobile = options.mobile;
  state.pip = options.pip;
  state.background = options.background;
  state.diagnostics = !!options.diagnostics;
  state.adjust();
  // Fixed booleans/counts only; no URL/title/config/video ID or page-provided strings.
  return {mobile:!!state.mobile,pip:!!state.pip,background:!!state.background,
    pipAdjusted:!!state.pipAdjusted,backgroundApplied:!!(state.mobile && state.background && state.backgroundInstalled && isPlaying()),pauseObserved:state.pauses>0,
    visibilityObserved:state.visibilityEvents>0,pauseMethodObserved:!!state.pauseMethodObserved,
    pauseWithActivation:!!state.pauseWithActivation,
    paused:!!document.querySelector('video')?.paused};
})()
