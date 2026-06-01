const { GuidanceAPI } = require('../../utils/api')
Page({
  data: {
    currentStudent: null,
    guidances: [],
    generating: false,
    showDetail: false,
    detailItems: [],
    detailLabels: {
      title: '标题', summary: '综合评估', study_advice: '学习建议',
      life_advice: '生活建议', parent_tips: '给家长的建议',
      weekly_goal: '本周目标', encouragement: '鼓励',
      overall_assessment: '整体评估', strengths: '优势', weaknesses: '薄弱知识点',
      study_plan: '学习计划', parent_advice: '家长建议',
    },
  },

  onShow() {
    const app = getApp()
    const student = app.globalData.currentStudent
    if (student) {
      this.setData({ currentStudent: student })
      this.loadGuidances(student.id)
    }
  },

  async loadGuidances(studentId) {
    const guidances = await GuidanceAPI.list(studentId)
    if (guidances) {
      this.setData({ guidances })
    }
  },

  async onGenerateAI() {
    if (!this.data.currentStudent) return
    this.setData({ generating: true })
    const result = await GuidanceAPI.aiGenerate(this.data.currentStudent.id)
    this.setData({ generating: false })
    if (result) {
      wx.showToast({ title: '新指导已生成' })
      this.loadGuidances(this.data.currentStudent.id)
    }
  },

  onViewDetail(e) {
    const content = e.currentTarget.dataset.content
    if (content[0] !== '{') return
    try {
      const data = JSON.parse(content)
      const items = Object.entries(data).filter(([k]) => k !== 'title')
      this.setData({ detailItems: items, showDetail: true })
    } catch(e) {
      // not JSON, ignore
    }
  },

  onCloseDetail() {
    this.setData({ showDetail: false })
  },
})
