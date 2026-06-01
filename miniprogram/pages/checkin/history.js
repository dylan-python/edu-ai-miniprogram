const { CheckinAPI } = require('../../../utils/api')

Page({
  data: {
    studentId: 0,
    checkins: [],
    days: 30,
    hasMore: true,
  },

  onLoad(options) {
    const studentId = parseInt(options.studentId)
    this.setData({ studentId })
    this.loadHistory()
  },

  async loadHistory() {
    const checkins = await CheckinAPI.history(this.data.studentId, this.data.days)
    if (checkins) {
      this.setData({
        checkins,
        hasMore: checkins.length >= this.data.days,
      })
    }
  },

  onLoadMore() {
    this.setData({ days: this.data.days + 30 })
    this.loadHistory()
  },
})
