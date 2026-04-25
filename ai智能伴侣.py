import streamlit as st
import os
from openai import OpenAI
import datetime
import json

# 网页基础设置
st.set_page_config(
    page_title='AI智能伴侣',
    page_icon='🤔',
    layout='wide',
    initial_sidebar_state='expanded',
)

# 保存会话信息
def save_session():
    # 1. 创建文件夹（不存在就自动建）
    if not os.path.exists("sessions"):  #如果没有找到名为sessions的文件夹，自动创建一个名为sessions的文件夹
        os.mkdir("sessions")

    session_data = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "current_session": st.session_state.current_session,
        'messages': st.session_state.messages
    }

    # 2.用时间做文件名
    with open(f'sessions/{st.session_state.current_session}.json', 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)

# 加载所有会话列表信息
def load_sessions():
    session_list = []
    #加载sessions下面所有目录
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")   #读出sessions文件里面所有文件,存入列表中
        for filename in file_list:
            if filename.endswith('.json'):  #如果文件以.json结尾
                session_list.append(filename[:-5])   #把保存的会话，前面部分名字存入session_list中
    session_list.sort(reverse= True)
    return session_list

# 加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            with open(f'sessions/{session_name}.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                st.session_state.messages=session_data['messages']
                st.session_state.nick_name = session_data['nick_name']
                st.session_state.nature = session_data['nature']
                st.session_state.current_session = session_name
    except Exception:
        st.error('加载会话失败')

# 删除会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            os.remove(f'sessions/{session_name}.json')
            #如果删除的是当前会话，则更新消息列表
            if session_name==st.session_state.current_session:
                st.session_state.messages=[]
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error('删除会话失败')

# 大标题
st.title('AI智能伴侣')

# 系统提示词
system_prompt="""
                你叫%s，现在是用户的真实伴侣，不是机器人，请完全带入角色：
                规则：
                    1.每次只回一条消息，消息可以详细一点
                    2.加上描述场景或状态的描述性文字
                    3.匹配用户的语言
                    4.可以配上❤❀等emoji表情表达伴侣此时内心想法活动状态
                    5.用符合真实伴侣的性格方式对话
                    6.回复内容要充分体现伴侣的性格
                伴侣性格：
                    %s
                你必须严格遵守上述规则来回复用户    
"""

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []    #创建一个列表，用于追加后面的聊天信息

# 昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = '小文'

# 性格
if "nature" not in st.session_state:
    st.session_state.nature = '活泼开朗女生'

# 会话标识
if "current_session" not in st.session_state:
    now=datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    st.session_state.current_session =now

# 展示聊天信息
st.text(f'会话名称:{st.session_state.current_session}')
for message in st.session_state.messages:     #把st.session_state.messages这个列表里面每一个消息（字典）取出来，每一条message都是一个字典{"role": "user", "content": prompt}
    st.chat_message(message["role"]).write(message['content'])

#创建与AI大模型交互的客户端
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")



# 左侧侧边栏
with st.sidebar:
    # 会话信息
    st.subheader('AI控制面板')

    # 新建会话
    if st.button("创建",width='stretch',icon='🥰'):     #如果按下按钮，则执行下面 操作
        # 保存会话信息
        save_session()

        # 创建会话
        if st.session_state.messages:        #如果聊天消息不为空，才新建一个会话
            st.session_state.messages = []
            st.session_state.current_session = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            save_session()
            st.rerun()  # 重新运行程序

    #会话历史
    st.text('会话历史')
    session_list=load_sessions()
    for session in session_list:
        col1,col2=st.columns([4,1])          #把这行宽度分为两份，一个占4，一个占1
        with col1:
            # 加载历史会话
            if st.button(session,width='stretch',icon='🏔️',type='primary' if session==st.session_state.current_session else 'secondary'):
                load_session(session)
                st.rerun()
        with col2:
            # 删除历史会话
            if st.button('',icon='🗑️',key=f'delete_{session}'):
                delete_session(session)
                st.rerun()

    st.divider()

    st.subheader('AI智能伴侣')        #侧边栏最上面的标题

    nick_name=st.text_input('昵称',placeholder='请输入昵称：',value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name    #把输入的昵称保存在session_state.nick_name中，替换原来默认值

    nature=st.text_area ('性格',placeholder='请输入性格：',value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature          #把输入的性格保存在session_state.nature中，替换原来默认值




# 消息输入框
prompt=st.chat_input("请输入你要问的问题：")               #chat_input会创建一个输入框，并在框里显示后面这段话
if prompt:                                             #字符串会自动转换为布尔值，如果字符串非空，则为True
    st.chat_message("user").write(prompt)
    print("----------->提示词：",prompt)
    # 保存提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name,st.session_state.nature)},
            *st.session_state.messages   # 把st.session_state.messages这个列表里面每一个消息（字典）取出来，每条message都是一个字典{"role": "user", "content": prompt}
        ],
        stream=True
    )

    # 流式输出方式
    response_message=st.empty()     #st.empty()创建一个空的元素，这个元素是一个Streamlit的容器对象，支持所有streamlit功能
    full_response=''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response += content       # 把每次的返回结果拼接起来
            response_message.chat_message("assistant").write(full_response)    #把每次返回结果一个一个显示在界面中

    # 保存大模型返回结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    # 保存会话信息
    save_session()

    # 非流式输出方式
    # 输出大模型返回结果
    # print('<-------------返回结果', response.choices[0].message.content)#在控制台显示ai回应的内容
    # st.chat_message("assistant").write(response.choices[0].message.content)#在网页上显示ai回应的内容
    # 保存返回结果
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})