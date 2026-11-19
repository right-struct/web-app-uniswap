document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('postsContainer');
  if (!container) return;
  const search = document.getElementById('marketplaceSearchInput');
  let category = '', type = '';
  const make = (tag, cls, value) => { const el=document.createElement(tag); if(cls) el.className=cls; el.textContent=value || ''; return el; };
  async function load() {
    container.replaceChildren(make('p','posts-loading-msg','Loading listings…'));
    const params = new URLSearchParams(); if(search?.value.trim()) params.set('search',search.value.trim()); if(category) params.set('category',category); if(type) params.set('type',type);
    try {
      const response=await fetch(`/api/items/?${params}`); if(!response.ok) throw new Error(); const data=await response.json();
      container.replaceChildren();
      if(!data.items.length) { container.append(make('p','posts-empty-msg','No listings found.')); return; }
      data.items.forEach(item => {
        const card=make('article','post-card');
        if(item.image_url) { const wrap=make('div','post-image-wrapper',''); const img=document.createElement('img'); img.src=item.image_url; img.alt=item.title; img.className='post-image-placeholder'; wrap.append(img); card.append(wrap); }
        const info=make('div','post-info',''); info.append(make('p','post-desc',item.title),make('p','post-desc',item.description),make('span','post-price',`${item.type_display} · ${item.price ? item.price+' ₸' : item.category_display}`));
        const details=make('button','btn-categories','Details'); details.type='button'; details.addEventListener('click',()=>window.location.href=`/api/items/${item.id}/`); info.append(details); card.append(info); container.append(card);
      });
    } catch { container.replaceChildren(make('p','posts-empty-msg','Could not load listings. Please try again.')); }
  }
  document.getElementById('marketplaceSearchBtn')?.addEventListener('click',load);
  search?.addEventListener('keydown',e=>{if(e.key==='Enter')load();});
  document.querySelectorAll('.filter-pill').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.filter-pill').forEach(x=>x.classList.remove('active'));btn.classList.add('active');const value=btn.textContent.trim();type=value==='All'?'':value;load();}));
  document.querySelectorAll('.category-item').forEach(el=>el.addEventListener('click',()=>{category=el.dataset.category==='all'?'':el.dataset.category;load();}));
  load();
});
