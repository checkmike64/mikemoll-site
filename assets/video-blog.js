/* Video blog posts: player facade, chapter seeking, contents scroll-spy,
   copy link, reading progress, phone CTA bar and CTA click events.
   Progressive enhancement only: every link works without this file. */
(function(){
  var d=document;

  /* ---- YouTube facade: the thumbnail is a real link; a click swaps in a
     youtube-nocookie player. Chapter and timestamp links seek it. ---- */
  var box=d.querySelector('.vb-video'),vid=box&&box.getAttribute('data-yt'),frame=null;
  function load(start){
    if(!box||frame) return frame;
    frame=d.createElement('iframe');
    frame.src='https://www.youtube-nocookie.com/embed/'+vid+'?autoplay=1&rel=0&modestbranding=1&playsinline=1&enablejsapi=1'+(start?'&start='+start:'')+'&origin='+encodeURIComponent(location.origin);
    frame.title=box.getAttribute('data-title')||'YouTube video';
    frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.referrerPolicy='strict-origin-when-cross-origin';
    frame.setAttribute('allowfullscreen','');
    box.innerHTML='';box.appendChild(frame);
    return frame;
  }
  function cmd(f,args){if(frame&&frame.contentWindow){frame.contentWindow.postMessage(JSON.stringify({event:'command',func:f,args:args||[]}),'*')}}
  if(box){box.addEventListener('click',function(e){if(frame)return;e.preventDefault();load(0)})}
  [].slice.call(d.querySelectorAll('a[data-t]')).forEach(function(a){
    a.addEventListener('click',function(e){
      if(!box) return;
      e.preventDefault();
      var t=parseInt(a.getAttribute('data-t'),10)||0;
      if(frame){cmd('seekTo',[t,true]);cmd('playVideo')}else{load(t)}
      var top=box.getBoundingClientRect().top+window.pageYOffset-24;
      window.scrollTo({top:top,behavior:'smooth'});
    });
  });

  /* ---- contents: open on desktop, collapsed on phones; scroll-spy ---- */
  var toc=d.querySelector('.vb-toc details');
  if(toc&&window.matchMedia){
    var mq=matchMedia('(min-width:901px)');
    toc.open=mq.matches;
    toc.addEventListener('click',function(e){var l=e.target.closest&&e.target.closest('a');if(l&&!mq.matches)toc.open=false});
    var links=[].slice.call(toc.querySelectorAll('a'));
    if('IntersectionObserver' in window){
      var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(l){l.classList.toggle('on',l.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'-20% 0px -65% 0px'});
      links.forEach(function(l){var s=d.getElementById(l.getAttribute('href').slice(1));if(s)io.observe(s)});
    }
  }

  /* ---- copy link ---- */
  var cp=d.querySelector('.vb-copy');
  if(cp) cp.addEventListener('click',function(){
    var u=cp.getAttribute('data-url');
    function done(){cp.textContent='Link copied';setTimeout(function(){cp.textContent='Copy link'},1800)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(done,function(){})}
  });

  /* ---- CTA clicks: one dataLayer event, tagged with the placement ---- */
  window.dataLayer=window.dataLayer||[];
  [].slice.call(d.querySelectorAll('[data-cta]')).forEach(function(a){
    a.addEventListener('click',function(){window.dataLayer.push({event:'blog_cta_click',cta_position:a.getAttribute('data-cta'),page_path:location.pathname})});
  });

  /* ---- reading progress + phone CTA bar (shows once the hero is passed) ---- */
  var bar=d.createElement('div');bar.id='vb-pgbar';bar.setAttribute('aria-hidden','true');d.body.appendChild(bar);
  var m=d.querySelector('.vb-mcta'),hero=d.querySelector('.vb-hero'),raf=false;
  function paint(){
    raf=false;
    var de=d.documentElement,max=de.scrollHeight-innerHeight,y=window.pageYOffset||de.scrollTop||0;
    bar.style.transform='scaleX('+(max>0?Math.min(1,y/max):0)+')';
    if(m&&hero){var show=hero.getBoundingClientRect().bottom<0;m.classList.toggle('show',show);m.setAttribute('aria-hidden',show?'false':'true');var a=m.querySelector('a');if(a)a.tabIndex=show?0:-1}
  }
  function on(){if(!raf){raf=true;requestAnimationFrame(paint)}}
  addEventListener('scroll',on,{passive:true});addEventListener('resize',on,{passive:true});paint();
})();
