# ima skills

统一的 IMA OpenAPI 技能，支持笔记管理和知识库操作。

## 功能

- **笔记管理**：搜索、浏览、创建、编辑笔记
- **知识库操作**：上传文件、添加网页、搜索知识库

## 安装

1. 访问 https://ima.qq.com/agent-interface 获取 Client ID 和 API Key
2. 配置凭证：
   ```bash
   mkdir -p ~/.config/ima
   echo "your_client_id" > ~/.config/ima/client_id
   echo "your_api_key" > ~/.config/ima/api_key
   ```

## 使用方法

### 笔记相关
- 「搜索笔记 XXX」
- 「创建新笔记」
- 「添加到笔记 XX」

### 知识库相关
- 「上传文件到知识库」
- 「添加网页到知识库」
- 「搜索知识库 XXX」

## API 文档

Base URL: `https://ima.qq.com`

详细文档请参考 SKILL.md
