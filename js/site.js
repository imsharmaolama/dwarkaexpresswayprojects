/* ===== Dwarka Expressway Projects — shared site JS ===== */
(function(){
  const PHONE = "9015883288";
  const PHONE_FULL = "+919015883288";
  const LEAD_EMAIL = "sharma.manish53@gmail.com";
  const PROJECTS = window.__PROJECTS__ || [];
  const EMAIL_RE = /^[\w.+-]+@[\w-]+\.[\w.-]+$/;

  /* ---------- IP-based country code (flag + dial, local number only) ---------- */
  async function applyCountryCode(){
    try{
      const r = await fetch('https://ipapi.co/json/');
      const d = await r.json();
      const code = (d.country_calling_code || d.calling_code || '+91').toString().replace(/\s/g,'');
      const iso = (d.country_code || 'IN').toLowerCase();
      const flag = 'https://flagcdn.com/24x18/'+iso+'.png';
      document.querySelectorAll('#ccCode').forEach(el=>el.textContent = code);
      document.querySelectorAll('#ccFlagImg').forEach(el=>{ el.src = flag; el.alt = (d.country_name||'country'); });
      document.querySelectorAll('#ccFlag').forEach(el=>el.title = d.country_name||'');
    }catch(e){ /* default +91 / India stays */ }
  }
  applyCountryCode();

  /* ---------- mobile menu ---------- */
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  if(toggle && nav){ toggle.addEventListener('click',()=>{ nav.classList.toggle('open'); }); }

  /* ---------- search overlay ---------- */
  const openSearch = ()=>{ const m=document.getElementById('searchModal'); if(m){ m.classList.add('open'); const i=m.querySelector('input'); if(i) i.focus(); } };
  const closeSearch = ()=>{ const m=document.getElementById('searchModal'); if(m) m.classList.remove('open'); };
  document.querySelectorAll('[data-search-open]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();openSearch();}));
  const sb = document.getElementById('searchBox');
  const sr = document.getElementById('searchResults');
  if(sb && sr){
    const render = q=>{
      q=q.trim().toLowerCase();
      if(!q){ sr.innerHTML=''; return; }
      const hits = PROJECTS.filter(p=> (p.name+' '+(p.location&&p.location.address||'')+' '+(p.configuration||'')).toLowerCase().includes(q)).slice(0,12);
      sr.innerHTML = hits.length ? hits.map(p=>{
        const img=(p.images&&p.images[0]&&p.images[0].image&&p.images[0].image.s3_link)||'';
        const loc=(p.location&&p.location.address)||'';
        return `<a href="projects/${p.file}.html"><img src="${img}" alt="${p.name}" loading="lazy"><div><div class="s-name">${p.name}</div><div class="s-loc">${loc} &middot; ${p.starting_price||''}</div></div></a>`;
      }).join('') : '<p style="padding:10px;color:#566b63">No projects found.</p>';
    };
    sb.addEventListener('input',e=>render(e.target.value));
  }

  /* ---------- enquiry modal ---------- */
  const enqModal = document.getElementById('enqModal');
  const enqTitle = document.getElementById('enqTitle');
  const enqProject = document.getElementById('enqProject');
  window.openEnquiry = (name)=>{
    if(enqModal){ enqTitle.textContent = name?('Enquire: '+name):'Enquire Now'; enqProject.value=name||''; enqModal.classList.add('open'); }
  };
  window.closeEnquiry = ()=>{ if(enqModal) enqModal.classList.remove('open'); };
  document.querySelectorAll('[data-enquire]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();window.openEnquiry(b.getAttribute('data-enquire'));}));

  /* ---------- gallery lightbox ---------- */
  const lb=document.getElementById('lightbox'); const lbImg=document.getElementById('lbImg');
  window.openLightbox=(src)=>{ if(lb){ lbImg.src=src; lb.classList.add('open'); } };
  window.closeLightbox=()=>{ if(lb) lb.classList.remove('open'); };
  if(lb) lb.addEventListener('click',window.closeLightbox);

  /* ---------- toast ---------- */
  const toast=(msg)=>{ let t=document.getElementById('toast'); if(!t){t=document.createElement('div');t.id='toast';t.className='toast';document.body.appendChild(t);} t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),3400); };

  /* ---------- send lead to email (FormSubmit) ---------- */
  async function sendLeadEmail(data){
    const body = `Name: ${data.name}\nEmail: ${data.email}\nPhone: ${data.phone} (${data.cc})\nProject: ${data.project}\nPage: ${data.page}\nNote: ${data.note}\nDate: ${data.date} ${data.time}`;
    try{
      await fetch('https://formsubmit.co/'+LEAD_EMAIL, {
        method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'},
        body: JSON.stringify({ name:'Site Lead', subject:'New Enquiry: '+(data.project||'Website'), email: LEAD_EMAIL, message: body, _replyto: data.email })
      });
    }catch(e){ /* offline-safe */ }
  }

  /* ---------- lead submit ---------- */
  function getPhone(form){
    // phone field may be plain input or ip-based .phone-field wrapper
    const pf = form.querySelector('.phone-field input');
    if(pf){ const cc = (form.querySelector('#ccCode')||{}).textContent || '+91'; const num = pf.value.trim(); return { num, cc, full: cc.replace(/\s/g,'')+num }; }
    const plain = form.phone; if(plain) return { num: plain.value.trim(), cc:'+91', full: '+91'+plain.value.trim() };
    return { num:'', cc:'+91', full:'' };
  }
  async function submitLead(form, extra){
    const ph = getPhone(form);
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: ph.full,
      cc: ph.cc,
      note: (form.note && form.note.value.trim())||'',
      page: location.href,
      project: extra && extra.project || (form.project && form.project.value)||'',
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString()
    };
    if(!data.name || !EMAIL_RE.test(data.email) || !/^\d{6,14}$/.test(ph.num.replace(/[^\d]/g,''))){
      toast('Please enter a valid name, email & phone number.'); return false;
    }
    await sendLeadEmail(data);
    return true;
  }
  document.querySelectorAll('form[data-lead]').forEach(form=>{
    form.addEventListener('submit',async e=>{
      e.preventDefault();
      const ok=await submitLead(form,{project:form.project&&form.project.value});
      if(ok){
        form.reset();
        showThanks();
        if(enqModal) enqModal.classList.remove('open');
        if(pendingDownload){ const u=pendingDownload; pendingDownload=null; setTimeout(()=>window.open(u,'_blank'),600); }
      }
    });
  });

  /* ---------- thank-you overlay: show 5s then return to same page ---------- */
  function ensureThanks(){
    let t=document.getElementById('thanksOverlay');
    if(!t){
      t=document.createElement('div');
      t.id='thanksOverlay';t.className='thanks-overlay';
      t.innerHTML='<div class="thanks-card"><div class="tcheck"><i class="fas fa-check"></i></div>'
        +'<h2>Thank You!</h2><p>Our expert will call you shortly with exclusive offers.</p>'
        +'<p class="tcount">Redirecting back in <span id="tCount">5</span>s…</p></div>';
      document.body.appendChild(t);
    }
    return t;
  }
  function showThanks(){
    const t=ensureThanks();
    t.classList.add('show');
    let n=5; const c=t.querySelector('#tCount'); if(c)c.textContent=n;
    clearInterval(window.__tTimer);
    window.__tTimer=setInterval(()=>{ n--; if(c)c.textContent=n; if(n<=0){ clearInterval(window.__tTimer); t.classList.remove('show'); } },1000);
  }

  /* ---------- hide any straggler broken images (dead external icons) ---------- */
  document.querySelectorAll('img').forEach(img=>{
    img.addEventListener('error',()=>{ img.style.display='none'; });
  });

  /* ---------- newsletter ---------- */
  document.querySelectorAll('form[data-newsletter]').forEach(form=>{
    form.addEventListener('submit',e=>{ e.preventDefault(); toast('Subscribed! We will keep you updated.'); form.reset(); });
  });

  /* ---------- lead-gate downloads (master plan / brochure) ---------- */
  /* open the SAME enquiry modal; after submit + thank-you, trigger the download */
  let pendingDownload = null;
  document.querySelectorAll('.lead-gate').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      pendingDownload = btn.getAttribute('data-url');
      const project = btn.getAttribute('data-enquire') || '';
      window.openEnquiry(project ? (project+' — '+btn.getAttribute('data-label')) : 'Download '+btn.getAttribute('data-label'));
    });
  });
  // after a successful lead submit, fire any pending download

  /* ---------- close on escape ---------- */
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ closeSearch(); window.closeEnquiry&&window.closeEnquiry(); window.closeLightbox&&window.closeLightbox(); }});
  document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>{ const t=b.getAttribute('data-close'); if(t==='search')closeSearch(); if(t==='enq')window.closeEnquiry(); }));

  /* ---------- GSAP scroll reveals (frontend-design / gsap-core) ---------- */
  (function(){
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const els = document.querySelectorAll('.best_project_heading, .section-sub, .project_card, .trust-item, .footer-col, .footer-news');
    els.forEach(el=>el.classList.add('reveal'));           // .reveal is opacity:1 by default (safe)
    // HARD SAFETY: never leave content hidden, even if GSAP/ScrollTrigger misbehave
    const safety = setTimeout(()=>els.forEach(el=>{el.style.opacity='';el.style.transform='';}), 1600);
    if(reduce || !window.gsap || !window.ScrollTrigger){ clearTimeout(safety); els.forEach(el=>el.classList.add('in')); return; }
    const gsap = window.gsap;
    gsap.registerPlugin(window.ScrollTrigger);
    document.documentElement.classList.add('gsap-ready');
    try{
      const hero = document.querySelector('.hero');
      if(hero) gsap.from(hero.querySelectorAll('.badges, h1, p.lead, .search-wrap'),
        {y:30, opacity:0, duration:.8, ease:'power3.out', stagger:.12});
      gsap.utils.toArray('.section').forEach(sec=>{
        const head = sec.querySelectorAll('.best_project_heading, .section-sub');
        if(head.length) gsap.from(head,{y:24,opacity:0,duration:.7,ease:'power3.out',scrollTrigger:{trigger:sec,start:'top 85%',once:true}});
        const cards = sec.querySelectorAll('.project_card');
        if(cards.length) gsap.from(cards,{y:34,opacity:0,duration:.6,ease:'power2.out',stagger:.08,scrollTrigger:{trigger:sec,start:'top 90%',once:true}});
      });
      gsap.utils.toArray('.trust-item, .footer-col').forEach((el,i)=>{
        gsap.from(el,{y:20,opacity:0,duration:.6,ease:'power2.out',delay:(i%3)*.08,scrollTrigger:{trigger:el,start:'top 92%',once:true}});
      });
      window.addEventListener('load', ()=>window.ScrollTrigger.refresh());
    }catch(e){ /* safety timer reveals everything */ }
  })();
})();
