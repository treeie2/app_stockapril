-- ============================================================
-- Supabase Schema for Stock Research Database
-- Run this in Supabase SQL Editor (https://supabase.com/dashboard)
-- ============================================================

-- 1. stocks 表 - 个股主数据
CREATE TABLE IF NOT EXISTS stocks (
  code TEXT PRIMARY KEY,                    -- 股票代码，如 "000001"
  name TEXT NOT NULL,                       -- 股票名称
  board TEXT DEFAULT '',                    -- 板块：SH/SZ/BJ
  industry TEXT DEFAULT '',                 -- 行业分类
  concepts JSONB DEFAULT '[]'::jsonb,       -- 概念标签
  products JSONB DEFAULT '[]'::jsonb,       -- 产品列表
  core_business JSONB DEFAULT '[]'::jsonb,  -- 核心业务
  industry_position JSONB DEFAULT '[]'::jsonb, -- 行业地位
  chain JSONB DEFAULT '[]'::jsonb,          -- 产业链位置
  partners JSONB DEFAULT '[]'::jsonb,       -- 合作伙伴
  mention_count INTEGER DEFAULT 0,          -- 提及次数
  last_updated TEXT DEFAULT '',             -- 最后更新日期
  articles JSONB DEFAULT '[]'::jsonb,       -- 文章列表
  detail_texts JSONB DEFAULT '[]'::jsonb,   -- 详细文本
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. groups 表 - 股票分组
CREATE TABLE IF NOT EXISTS groups_data (
  id TEXT PRIMARY KEY,                      -- 分组ID：group_20260601xxx
  name TEXT NOT NULL,                        -- 分组名称
  description TEXT DEFAULT '',               -- 分组描述
  color TEXT DEFAULT '#3b82f6',             -- 颜色
  icon TEXT DEFAULT '📁',                   -- 图标
  stocks JSONB DEFAULT '[]'::jsonb,         -- 股票名称列表
  created_at TEXT DEFAULT '',                -- 创建日期
  updated_at TEXT DEFAULT ''                 -- 更新日期
);

-- 3. hot_topics 表 - 市场热点话题
CREATE TABLE IF NOT EXISTS hot_topics (
  id TEXT PRIMARY KEY,                      -- 热点ID：topic_20260506xxx
  name TEXT NOT NULL,                       -- 热点名称
  drivers TEXT DEFAULT '',                   -- 驱动因素
  stocks JSONB DEFAULT '[]'::jsonb,         -- 相关股票
  display BOOLEAN DEFAULT true,              -- 是否显示
  created_at TEXT DEFAULT '',
  updated_at TEXT DEFAULT ''
);

-- ============================================================
-- Row Level Security (RLS)
-- ============================================================
ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE hot_topics ENABLE ROW LEVEL SECURITY;

-- 允许公开读取（前端查询不用登录）
CREATE POLICY IF NOT EXISTS "public can read stocks" 
  ON stocks FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "public can read groups_data" 
  ON groups_data FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "public can read hot_topics" 
  ON hot_topics FOR SELECT USING (true);

-- ============================================================
-- 索引
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_stocks_name ON stocks (name);
CREATE INDEX IF NOT EXISTS idx_stocks_industry ON stocks (industry);
CREATE INDEX IF NOT EXISTS idx_stocks_last_updated ON stocks (last_updated);
CREATE INDEX IF NOT EXISTS idx_groups_name ON groups_data (name);
CREATE INDEX IF NOT EXISTS idx_hot_topics_name ON hot_topics (name);
CREATE INDEX IF NOT EXISTS idx_hot_topics_display ON hot_topics (display);