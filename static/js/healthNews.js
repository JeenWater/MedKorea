document.addEventListener('DOMContentLoaded', () => {
    fetch('http://localhost:9119/api/health-news')
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(Array.isArray(data)){
                displayArticles(data, 4);
            }else if (data.articles){
                displayArticles(data.articles, 4);
            }else{
                console.error('No articles found or data is not in expected format:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching health news:', error);
        });
});

let currentIndex = 0;
let displayedArticles = [];

function displayArticles(articles, count) {
    const newsContainer = document.querySelector('.health-news-articles');

    const articlesToShow = articles.slice(currentIndex, currentIndex + count);

    articlesToShow.forEach(article => {
        const articleDiv = document.createElement('li');
        articleDiv.classList.add('article');

        if(article.urlToImage){
            articleDiv.innerHTML = `
                <div class="article-img">
                    <img src="${article.urlToImage}" alt="Article Image" />
                </div>
                <div class="article-txt">
                    <h3 class="headline">${article.title}</h3>
                    <p class="summary">${article.description || 'No description available.'}</p>
                    <p><small>Published at: ${new Date(article.publishedAt).toLocaleString()}</small></p>
                </div>
            `;
        }else{
            articleDiv.innerHTML = `
                <div class="article-txt">
                    <h3 class="headline">${article.title}</h3>
                    <p class="summary">${article.description || 'No description available.'}</p>
                    <p><small>Published at: ${new Date(article.publishedAt).toLocaleString()}</small></p>
                </div>
            `;
        }
        newsContainer.appendChild(articleDiv);

        const headline = articleDiv.querySelector('.headline');

        headline.addEventListener('click', () => {
            document.getElementById('modalTitle').textContent = article.title;
            document.getElementById('modalDescription').textContent = article.description || 'No description available.';
            document.getElementById('modalPublishedAt').textContent = `Published at: ${new Date(article.publishedAt).toLocaleString()}`;

            const modalImage = document.getElementById('modalImage');
            if (article.urlToImage) {
                modalImage.src = article.urlToImage;
                modalImage.style.display = 'block';
            }else{
                modalImage.style.display = 'none';
            }

            document.getElementById('myModal').style.display = 'block';
        });

        displayedArticles.push(articleDiv);
    });

    currentIndex += count;

    const modal = document.getElementById('myModal');
    const closeModal = document.querySelector('.modal .close');
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    const existingReadMoreBtn = document.querySelector('.read-more-Btn');
    const existingReadLessBtn = document.querySelector('.read-less-Btn');
    if (existingReadMoreBtn) existingReadMoreBtn.remove();
    if (existingReadLessBtn) existingReadLessBtn.remove();

    let btns = document.querySelector('.btns');
    if(!btns){
        btns = document.createElement('div');
        btns.className = 'btns';
        btns.style.display = 'flex';
        btns.style.justifyContent = 'space-between';
        const healthNews = document.querySelector('.health-news');
        healthNews.appendChild(btns);
    }

    // Read More
    if(currentIndex < articles.length){
        const readMoreBtn = document.createElement('button');
        readMoreBtn.textContent = 'Read More';
        readMoreBtn.classList.add('read-more-Btn');
        btns.appendChild(readMoreBtn);

        readMoreBtn.addEventListener('click', () => {
            displayArticles(articles, 4);
        });
    }

    // Read Less
    if(displayedArticles.length > 4){
        const readLessBtn = document.createElement('button');
        readLessBtn.textContent = 'Read Less';
        readLessBtn.classList.add('read-less-Btn');
        btns.appendChild(readLessBtn);

        readLessBtn.addEventListener('click', () => {
            const articlesToHide = displayedArticles.slice(-count);
            articlesToHide.forEach(article => {
                article.remove();
            });
            displayedArticles = displayedArticles.slice(0, -count);
            currentIndex -= count;

            if(currentIndex <= count){
                readLessBtn.remove();
            }

            if(currentIndex < articles.length && !document.querySelector('.read-more-Btn')){
                const readMoreBtn = document.createElement('button');
                readMoreBtn.textContent = 'Read More';
                readMoreBtn.classList.add('read-more-Btn');
                btns.appendChild(readMoreBtn);

                readMoreBtn.addEventListener('click', () => {
                    displayArticles(articles, 4);
                });
            }
        });
    }
}