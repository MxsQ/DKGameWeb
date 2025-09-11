// 侧边栏导航功能
document.addEventListener('DOMContentLoaded', function() {
    // 仅选择带有 data-page 的导航链接
    const navLinks = document.querySelectorAll('.nav-link[data-page]');
    const contentContainer = document.getElementById('content-container');
    
    // 为每个导航链接添加点击事件
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 对于需要整页渲染的页面，允许正常跳转
            if (this.getAttribute('data-page') === 'data-details' || this.getAttribute('data-page') === 'game-overview') {
                return; // 不阻止默认行为，允许正常跳转
            }
            
            e.preventDefault();
            
            // 移除所有活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            
            // 获取页面标识
            const page = this.getAttribute('data-page');
            
            // 根据页面标识加载相应内容
            loadPageContent(page);
        });
    });
    
    // 页面加载完成后，设置当前页面的导航状态
    setCurrentPageActive();
});

// 加载页面内容
function loadPageContent(page) {
    const contentContainer = document.getElementById('content-container');
    
    // 显示加载状态
    contentContainer.innerHTML = '<div class="loading">加载中...</div>';
    
    // 根据页面类型加载不同内容
    switch(page) {
        case 'game-overview':
            loadGameOverview();
            break;
        case 'data-details':
            loadDataDetails();
            break;
        case 'channel-analysis':
            // 对于渠道分析页面，允许正常跳转
            window.location.href = '/channel-analysis';
            return;
        default:
            contentContainer.innerHTML = '<div class="no-data">页面不存在</div>';
    }
}

// 加载游戏概览内容
function loadGameOverview() {
    fetch('/api/games')
        .then(response => response.json())
        .then(games => {
            const contentContainer = document.getElementById('content-container');
            
            if (games.length > 0) {
                let html = `
                    <div class="page-header">
                        <h2>游戏概览</h2>
                        <p>查看所有游戏的详细统计信息</p>
                    </div>
                    <div class="games-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>游戏名称</th>
                                    <th>总玩家数</th>
                                    <th>活跃玩家</th>
                                    <th>收入</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                games.forEach(game => {
                    html += `
                        <tr>
                            <td>${game.name}</td>
                            <td>${game.total_players}</td>
                            <td>${game.active_players}</td>
                            <td>¥${game.revenue.toFixed(2)}</td>
                        </tr>
                    `;
                });
                
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
                
                contentContainer.innerHTML = html;
            } else {
                contentContainer.innerHTML = '<div class="no-data">暂无游戏数据</div>';
            }
        })
        .catch(error => {
            console.error('加载游戏概览失败:', error);
            document.getElementById('content-container').innerHTML = '<div class="no-data">加载失败，请稍后重试</div>';
        });
}

// 加载数据详情内容
function loadDataDetails() {
    fetch('/api/games')
        .then(response => response.json())
        .then(games => {
            const contentContainer = document.getElementById('content-container');
            
            if (games.length > 0) {
                let html = `
                    <div class="page-header">
                        <h2>数据详情</h2>
                        <p>查看游戏的详细数据指标</p>
                    </div>
                    <div class="data-details">
                `;
                
                games.forEach(game => {
                    html += `
                        <div class="game-detail-section">
                            <h3>${game.name}</h3>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="label">总玩家数:</span>
                                    <span class="value">${game.total_players}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">活跃玩家:</span>
                                    <span class="value">${game.active_players}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">收入:</span>
                                    <span class="value">¥${game.revenue.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                contentContainer.innerHTML = html;
            } else {
                contentContainer.innerHTML = '<div class="no-data">暂无游戏数据</div>';
            }
        })
        .catch(error => {
            console.error('加载数据详情失败:', error);
            document.getElementById('content-container').innerHTML = '<div class="no-data">加载失败，请稍后重试</div>';
        });
}

// 设置当前页面的导航状态
function setCurrentPageActive() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
} 