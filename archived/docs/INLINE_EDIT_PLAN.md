# 内联编辑功能实现方案

## 目标
点击"编辑"按钮后，直接在页面上将只读文本转换为可编辑文本框，无需弹窗。

## 实现步骤

### 1. 添加 CSS 样式

```css
/* 编辑模式 */
.inline-edit-mode .editable-text {
    display: none;
}

.inline-edit-mode .editable-input {
    display: block;
}

.editable-input {
    display: none;
    width: 100%;
    min-height: 60px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 6px;
    padding: 0.6rem;
    color: var(--text-primary);
    font-size: 0.85rem;
    resize: vertical;
}

.editable-input:focus {
    outline: none;
    border-color: var(--accent-purple);
    background: rgba(139,92,246,0.15);
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1);
}

.edit-actions-bar {
    display: none;
    align-items: center;
    justify-content: flex-end;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(139,92,246,0.05);
    border-top: 1px solid rgba(139,92,246,0.2);
}

.inline-edit-mode .edit-actions-bar {
    display: flex;
}
```

### 2. 修改 HTML 结构

将每个可编辑字段包装为：

```html
<div class="editable-field" data-field="core_business">
    <div class="editable-text">
        <ul class="info-list">
            {% for item in stock.core_business %}
                <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    <textarea class="editable-input" 
              data-field="core_business">${(data.core_business || []).join('\n')}</textarea>
</div>
```

### 3. JavaScript 逻辑

```javascript
function toggleEditMode() {
    const container = document.querySelector('.container');
    const editBtn = document.querySelector('.edit-btn-hero');
    
    container.classList.toggle('inline-edit-mode');
    
    if (container.classList.contains('inline-edit-mode')) {
        // 进入编辑模式
        editBtn.textContent = '✖ 取消编辑';
        editBtn.onclick = cancelEdit;
        
        // 填充文本框
        document.querySelectorAll('.editable-field').forEach(field => {
            const fieldName = field.dataset.field;
            const textarea = field.querySelector('.editable-input');
            const textDiv = field.querySelector('.editable-text');
            
            // 获取当前值（从 ul li 或 .pill 等）
            let currentValue = '';
            if (textDiv.querySelector('ul')) {
                currentValue = Array.from(textDiv.querySelectorAll('li'))
                    .map(li => li.textContent).join('\n');
            } else if (textDiv.querySelector('.pill')) {
                currentValue = Array.from(textDiv.querySelectorAll('.pill'))
                    .map(pill => pill.textContent).join('\n');
            }
            
            textarea.value = currentValue;
        });
        
        // 显示操作栏
        document.querySelector('.edit-actions-bar').style.display = 'flex';
    } else {
        // 退出编辑模式
        editBtn.textContent = '✏️ 编辑';
        editBtn.onclick = toggleEditMode;
    }
}

function cancelEdit() {
    toggleEditMode();
}

function saveEdit() {
    const data = {};
    document.querySelectorAll('.editable-field').forEach(field => {
        const fieldName = field.dataset.field;
        const textarea = field.querySelector('.editable-input');
        
        // 按行分割，过滤空行
        const values = textarea.value.split('\n')
            .map(line => line.trim())
            .filter(line => line);
        
        data[fieldName] = values;
    });
    
    // 发送到后端
    fetch(`/api/stock/${code}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(result => {
        if (result.success) {
            // 刷新页面或更新显示
            location.reload();
        } else {
            alert('保存失败：' + result.error);
        }
    });
}
```

## 优点

1. **直观**：直接在原位置编辑，无需弹窗
2. **简洁**：不需要复杂的 Tab 切换
3. **快速**：一次编辑多个字段，统一保存

## 缺点

1. **页面较长**：所有字段都展开
2. **无分类**：无法分组管理字段

## 替代方案

如果内联编辑太复杂，可以保留弹窗方案，但优化：
1. 增加字段预览
2. 支持实时保存
3. 添加撤销功能
