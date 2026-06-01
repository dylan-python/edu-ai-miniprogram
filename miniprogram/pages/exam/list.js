const { ExamAPI } = require('../../../utils/api')
Page({
  data: { studentId: 0, exams: [] },
  onLoad(options) {
    this.setData({ studentId: parseInt(options.studentId) })
    this.loadExams()
  },
  onShow() { this.loadExams() },
  onPullDownRefresh() { this.loadExams().then(() => wx.stopPullDownRefresh()) },
  async loadExams() {
    const exams = await ExamAPI.list(this.data.studentId)
    if (exams) this.setData({ exams })
  },
  onAddExam() {
    wx.navigateTo({ url: `/pages/exam/add/add?studentId=${this.data.studentId}` })
  },
  onExamDetail(e) {
    wx.navigateTo({ url: `/pages/exam/detail/detail?id=${e.currentTarget.dataset.id}` })
  },
  subjectClass(subject) {
    const map = {
      '语文': 'chinese', '数学': 'math', '英语': 'english',
      '科学': 'science', '道德与法治': 'ethics', '其他': 'other'
    }
    return map[subject] || 'other'
  },
})
