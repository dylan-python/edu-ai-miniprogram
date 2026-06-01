const { CheckinAPI } = require('../../utils/api')

Page({
  data: {
    studentId: 0,
    studentName: '',
    userAvatar: '👤',
    messages: [],
    inputText: '',
    isThinking: false,
    scrollTo: '',
    hasCompleted: false,
    suggestions: ['今天很开心', '今天学了数学和语文', '作业都做完了', '遇到了一道难题'],
    sessionData: {
      conversation_history: [],
      existing_data: {},
    },
  },

  onLoad(options) {
    const studentId = parseInt(options.studentId)
    const studentName = options.studentName || '同学'
    this.setData({ studentId, studentName })

    // 开场白
    const greeting = `你好呀，${studentName}！我是小智老师 🤗 今天在学校过得怎么样？有什么有趣的事情想跟我分享吗？`
    this.addMessage('assistant', greeting)
  },

  addMessage(role, content) {
    const now = new Date()
    const time = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
    const msg = { id: Date.now(), role, content, time }
    const messages = [...this.data.messages, msg]
    this.setData({ messages, scrollTo: 'msg-bottom' }, () => {
      this.setData({ scrollTo: '' })
    })
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value })
  },

  onSuggestion(e) {
    const text = e.currentTarget.dataset.text
    this.setData({ inputText: text })
    this.onSend()
  },

  async onSend() {
    const text = this.data.inputText.trim()
    if (!text || this.data.isThinking) return

    this.setData({ inputText: '' })
    this.addMessage('user', text)

    // 更新对话历史
    const history = this.data.sessionData.conversation_history || []
    history.push({ role: 'user', content: text })

    this.setData({ isThinking: true, suggestions: [] })

    try {
      const result = await CheckinAPI.aiChat(
        this.data.studentId,
        text,
        'checkin',
        this.data.sessionData
      )

      if (result) {
        this.addMessage('assistant', result.reply || '嗯嗯，继续说说吧~')

        // 更新 session 数据
        this.data.sessionData.conversation_history.push({
          role: 'assistant',
          content: result.reply,
        })
        if (result.structured_data) {
          Object.assign(this.data.sessionData.existing_data, result.structured_data)
        }

        // 如果打卡完成，提供打总结按钮的提示
        if (result.has_completed) {
          this.setData({
            hasCompleted: true,
            suggestions: ['好的，今天就到这里！', '再看一下今天的总结吧', '明天见！'],
          })
        } else if (result.suggestions && result.suggestions.length > 0) {
          this.setData({ suggestions: result.suggestions })
        } else {
          this.setData({
            suggestions: ['今天学了什么？', '作业做完了吗？', '今天开心吗？', '有什么困难吗？'],
          })
        }
      } else {
        this.addMessage('assistant', '哎呀，小智老师网络开小差了，能再说一遍吗？😅')
      }
    } catch (err) {
      this.addMessage('assistant', '小智老师遇到了一点小问题，稍等一下重新试试？🤔')
    }

    this.setData({ isThinking: false })
  },
})
