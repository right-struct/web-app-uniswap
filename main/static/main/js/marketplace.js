/**
 * UniSwap SDU - Marketplace Frontend Script
 * Connects frontend UI to Django REST API (/api/items/)
 * Handles Modal Popups, Filtering, and Search.
 */

document.addEventListener('DOMContentLoaded', function () {
  const postsContainer = document.getElementById('postsContainer');
  const authModal = document.getElementById('authModal');
  const closeModalBtn = document.getElementById('closeModal');
  const searchInput = document.getElementById('marketplaceSearchInput');
  const searchBtn = document.getElementById('marketplaceSearchBtn');
  const filterPills = document.querySelectorAll('.filter-pill');
  const categoryItems = document.querySelectorAll('.category-item');

  let currentCategory = '';
  let currentSearch = '';

  // 1. Mock item HTML to match Figma reference if database has no items yet
  const mockItems = [
    {
      title: 'iPad 2022 идеальное состояние братишка отвечаю самсой и полно...',
      price: '275 000 ₸',
      category: 'electronics'
    },
    {
      title: 'Calculus Early Transcendentals 8th Edition (Stewart)',
      price: 'Swap / 12 000 ₸',
      category: 'books'
    },
    {
      title: 'MacBook Air M1 8/256 Space Gray идеальный для учебы',
      price: '290 000 ₸',
      category: 'electronics'
    },
    {
      title: 'Худи SDU University Merch (Размер L, темно-синий)',
      price: '8 500 ₸',
      category: 'clothing'
    },
    {
      title: 'Наушники Sony WH-1000XM4 с шумоподавлением',
      price: 'Swap for iPad',
      category: 'electronics'
    },
    {
      title: 'Курс конспектов и лаб по Data Structures & Algorithms',
      price: 'Free / Swap',
      category: 'books'
    },
    {
      title: 'Репетиторство по линейной алгебре и диффурам',
      price: '3 500 ₸/час',
      category: 'services'
    },
    {
      title: 'Графический планшет Wacom One для дизайнеров',
      price: '25 000 ₸',
      category: 'electronics'
    },
    {
      title: 'SDU Engineering Рюкзак водонепроницаемый',
      price: '7 000 ₸',
      category: 'clothing'
    },
    {
      title: 'iPhone 13 128GB Midnight батарея 88%',
      price: '210 000 ₸',
      category: 'electronics'
    }
  ];

  // Helper to render an item card
  function createCardHTML(item) {
    const title = item.title || 'No Title';
    const desc = item.description || title;
    const categoryName = item.category_display || item.category || 'General';
    const priceOrContact = item.contact ? `${item.contact}` : (item.price || 'UniSwap');

    return `
      <div class="post-card js-open-modal" data-id="${item.id || ''}" title="${title}">
        <div class="post-image-wrapper">
          <img src="/static/main/img/ipad_card.png" class="post-image-placeholder" alt="${title}">
        </div>
        <div class="post-info">
          <p class="post-desc">${desc}</p>
          <span class="post-price">${priceOrContact}</span>
        </div>
      </div>
    `;
  }

  // 2. Fetch items from Django backend API
  async function loadItems() {
    if (!postsContainer) return;

    postsContainer.innerHTML = '<div class="posts-loading-msg">Loading marketplace items...</div>';

    try {
      let url = '/api/items/?';
      if (currentSearch) {
        url += `search=${encodeURIComponent(currentSearch)}&`;
      }
      if (currentCategory && currentCategory !== 'all') {
        url += `category=${encodeURIComponent(currentCategory)}&`;
      }

      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`HTTP error: ${res.status}`);
      }
      const data = await res.json();

      if (data.success && data.items && data.items.length > 0) {
        postsContainer.innerHTML = data.items.map(item => createCardHTML(item)).join('');
      } else {
        // Fallback: If DB is empty, render Figma reference cards so the page looks complete
        let filteredMock = mockItems;
        if (currentCategory && currentCategory !== 'all') {
          filteredMock = mockItems.filter(m => m.category === currentCategory);
        }
        if (currentSearch) {
          filteredMock = filteredMock.filter(m => m.title.toLowerCase().includes(currentSearch.toLowerCase()));
        }

        if (filteredMock.length > 0) {
          postsContainer.innerHTML = filteredMock.map(m => createCardHTML(m)).join('');
        } else {
          postsContainer.innerHTML = '<div class="posts-empty-msg">No items found matching your query.</div>';
        }
      }
    } catch (err) {
      console.warn('Backend API request failed, displaying reference items:', err);
      postsContainer.innerHTML = mockItems.map(m => createCardHTML(m)).join('');
    }
  }

  // 3. Search handling
  function triggerSearch() {
    if (searchInput) {
      currentSearch = searchInput.value.trim();
      loadItems();
    }
  }

  if (searchBtn) {
    searchBtn.addEventListener('click', triggerSearch);
  }

  if (searchInput) {
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        triggerSearch();
      }
    });
  }

  // 4. Category and Pill filtering
  filterPills.forEach(pill => {
    pill.addEventListener('click', function () {
      filterPills.forEach(p => p.classList.remove('active'));
      this.classList.add('active');

      const filterText = this.textContent.trim().toLowerCase();
      if (filterText === 'all') {
        currentCategory = '';
      } else if (filterText === 'swap' || filterText === 'sale' || filterText === 'looking' || filterText === 'free') {
        currentSearch = filterText;
      }
      loadItems();
    });
  });

  categoryItems.forEach(item => {
    item.addEventListener('click', function () {
      const cat = this.getAttribute('data-category') || '';
      currentCategory = (cat === 'all') ? '' : cat;
      loadItems();
    });
  });

  // 5. Modal Logic (Open / Close)
  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.js-open-modal');
    if (trigger && authModal) {
      authModal.classList.add('active');
    }
  });

  if (closeModalBtn && authModal) {
    closeModalBtn.addEventListener('click', function () {
      authModal.classList.remove('active');
    });
  }

  if (authModal) {
    authModal.addEventListener('click', function (e) {
      if (e.target === authModal) {
        authModal.classList.remove('active');
      }
    });
  }

  // Escape key closes modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && authModal && authModal.classList.contains('active')) {
      authModal.classList.remove('active');
    }
  });

  // Initial load
  loadItems();
});
