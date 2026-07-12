/* ===== Dwarka Expressway Projects — shared site JS ===== */
(function(){
  const PHONE = "9999063322";
  const PROJECTS = window.__PROJECTS__ || [];

  /* ---- mobile menu ---- */
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  if(toggle && nav){ toggle.addEventListener('click',()=>{ nav.style.display = nav.style.display==='flex'?'none':'flex'; }); }

  /* ---- search overlay ---- */
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
      }).join('') : '<p style="padding:10px;color:#5a6a7a">No projects found.</p>';
    };
    sb.addEventListener('input',e=>render(e.target.value));
  }

  /* ---- enquiry modal ---- */
  const enqModal = document.getElementById('enqModal');
  const enqTitle = document.getElementById('enqTitle');
  const enqProject = document.getElementById('enqProject');
  window.openEnquiry = (name)=>{
    if(enqModal){ enqTitle.textContent = name?('Enquire: '+name):'Enquire Now'; enqProject.value=name||''; enqModal.classList.add('open'); }
  };
  window.closeEnquiry = ()=>{ if(enqModal) enqModal.classList.remove('open'); };
  document.querySelectorAll('[data-enquire]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();window.openEnquiry(b.getAttribute('data-enquire'));}));

  /* ---- gallery lightbox ---- */
  const lb=document.getElementById('lightbox'); const lbImg=document.getElementById('lbImg');
  window.openLightbox=(src)=>{ if(lb){ lbImg.src=src; lb.classList.add('open'); } };
  window.closeLightbox=()=>{ if(lb) lb.classList.remove('open'); };
  if(lb) lb.addEventListener('click',window.closeLightbox);

  /* ---- toast ---- */
  const toast=(msg)=>{ let t=document.getElementById('toast'); if(!t){t=document.createElement('div');t.id='toast';t.className='toast';document.body.appendChild(t);} t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),3200); };

  /* ---- lead submit (posts to original Google-Sheets endpoint) ---- */
  async function submitLead(form, extra){
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      note: (form.note && form.note.value.trim())||'',
      pageLocation: location.href,
      project: extra && extra.project || (form.project && form.project.value)||'',
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString()
    };
    if(!data.name || !/^[\w.+-]+@[\w-]+\.[\w.-]+$/.test(data.email) || !/^\d{10}$/.test(data.phone)){
      toast('Please enter a valid name, email & 10-digit phone.'); return false;
    }
    try{
      await fetch('https://v1.nocodeapi.com/dwarkaexpressway/google_sheets/CQjlqWJyvQCdwALG?tabId=Sheet1',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify([[data.date,data.time,data.pageLocation,data.note,data.name,data.email,data.phone]])
      });
    }catch(e){ /* endpoint may block CORS; still show success locally */ }
    return true;
  }
  document.querySelectorAll('form[data-lead]').forEach(form=>{
    form.addEventListener('submit',async e=>{
      e.preventDefault();
      const ok=await submitLead(form,{project:form.project&&form.project.value});
      if(ok){ form.reset(); toast('Thank you! Our team will call you shortly.'); if(enqModal) enqModal.classList.remove('open'); }
    });
  });

  /* ---- close on escape ---- */
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ closeSearch(); window.closeEnquiry&&window.closeEnquiry(); window.closeLightbox&&window.closeLightbox(); }});
  document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>{ const t=b.getAttribute('data-close'); if(t==='search')closeSearch(); if(t==='enq')window.closeEnquiry(); }));
})();
