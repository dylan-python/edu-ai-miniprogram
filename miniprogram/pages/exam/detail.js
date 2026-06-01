const { ExamAPI } = require('../../../utils/api')
Page({
  data: { exam: null, analysis: null },
  onLoad(o) { this.loadExam(parseInt(o.id)) },
  async loadExam(id) {
    const exam = await ExamAPI.get(id)
    if (exam) {
      this.setData({ exam })
      if (exam.analysis) {
        try {
          const a = typeof exam.analysis === 'string' ? JSON.parse(exam.analysis) : exam.analysis
          this.setData({ analysis: a })
        } catch(e) {
          this.setData({ analysis: { overall_assessment: exam.analysis } })
        }
      }
    }
  },
})
