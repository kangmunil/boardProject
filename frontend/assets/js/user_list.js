document.addEventListener('DOMContentLoaded', async () => {
    const userListElement = document.getElementById('user-list');

    try {
        const response = await fetch('/api/users'); // 사용자 목록을 가져올 API 엔드포인트
        if (response.ok) {
            const users = await response.json();
            users.forEach(user => {
                const listItem = document.createElement('li');
                listItem.className = 'user-list-item'; // CSS 클래스 추가
                listItem.innerHTML = `
                    <span class="user-id">${user.id}</span>
                    <span class="user-name"><a href="/users/${user.id}">${user.username}</a></span>
                    <span class="user-email">${user.email}</span>
                    <span class="user-bio">${user.bio || ''}</span> <!-- bio 추가 -->
                    <span class="user-actions">
                        <button class="edit-btn" data-user-id="${user.id}">회원수정</button>
                        <button class="delete-btn" data-user-id="${user.id}">회원삭제</button>
                    </span>
                `;
                userListElement.appendChild(listItem);
            });
        } else {
            userListElement.innerHTML = '<li>사용자 목록을 불러오는데 실패했습니다.</li>';
        }
    } catch (error) {
        console.error('Error fetching user list:', error);
        userListElement.innerHTML = '<li>서버와 통신할 수 없습니다.</li>';
    }
});