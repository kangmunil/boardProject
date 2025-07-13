document.addEventListener('DOMContentLoaded', async () => {
    const userListElement = document.getElementById('user-list');

    try {
        const response = await fetch('/api/users'); // 사용자 목록을 가져올 API 엔드포인트
        if (response.ok) {
            const users = await response.json();
            users.forEach(user => {
                const listItem = document.createElement('li');
                listItem.textContent = `ID: ${user.id}, Username: ${user.username}, Email: ${user.email}`;
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