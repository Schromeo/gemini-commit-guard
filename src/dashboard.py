import streamlit as st
import sqlite3
import pandas as pd
import json

# 页面配置
st.set_page_config(page_title="Gemini Guard Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Gemini Commit Guard 监控台")

# 连接数据库
DB_PATH = ".gemini_audit.db"

def load_data():
    """从 SQLite 读取所有日志"""
    try:
        conn = sqlite3.connect(DB_PATH)
        # 读取所有数据，按时间倒序
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("📭 暂无审计记录。请先尝试进行几次 Git Commit。")
else:
    # --- 侧边栏：统计信息 ---
    st.sidebar.header("📊 审计概览")
    total_commits = len(df)
    pass_count = len(df[df['status'] == 'PASS'])
    fail_count = len(df[df['status'] == 'FAIL'])
    
    st.sidebar.metric("总提交次数", total_commits)
    st.sidebar.metric("✅ 通过", pass_count)
    st.sidebar.metric("🚨 拦截", fail_count)
    
    # 计算通过率
    if total_commits > 0:
        pass_rate = (pass_count / total_commits) * 100
        st.sidebar.progress(pass_rate / 100, text=f"通过率: {pass_rate:.1f}%")

    # --- 主界面：记录列表 ---
    st.subheader("🕒 历史记录")

    # 遍历每一行数据
    for index, row in df.iterrows():
        # 根据状态设置颜色
        status_color = "green" if row['status'] == 'PASS' else "red"
        icon = "✅" if row['status'] == 'PASS' else "🚨"
        
        with st.expander(f"{icon} [{row['timestamp']}] {row['message']}"):
            # 使用列布局
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 🔍 AI 诊断详情")
                try:
                    ai_json = json.loads(row['ai_response'])
                    st.json(ai_json)
                except:
                    st.text(row['ai_response'])

            with col2:
                st.markdown("#### 📝 代码变更 (Diff)")
                st.code(row['diff'], language='diff')
                
            if row['context']:
                 st.markdown("#### 📄 文件上下文")
                 with st.container(height=200): # 限制高度，可滚动
                     st.code(row['context'])

# 自动刷新按钮
if st.button("🔄 刷新数据"):
    st.rerun()