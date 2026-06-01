// pages/index/index.js
const { StudentAPI, CheckinAPI } = require('../../utils/api')

Page({
  data: {
    students: [],
    currentStudent: null,
    todayCheckin: null,
  },

  onLoad() {
    this.loadStudents()
  },

  onShow() {
    if (this.data.currentStudent) {
      this.loadTodayCheckin(this.data.currentStudent.id)
    }
  },

  onPullDownRefresh() {
    this.loadStudents().then(() => wx.stopPullDownRefresh())
  },

  async loadStudents() {
    const students = await StudentAPI.list()
    if (students) {
      this.setData({ students })
      // 自动选中第一个或之前选中的
      const app = getApp()
      if (app.globalData.currentStudent) {
        const curr = students.find(s => s.id === app.globalData.currentStudent.id)
        if (curr) {
          this.setData({ currentStudent: curr })
          this.loadTodayCheckin(curr.id)
          return
        }
      }
      if (students.length > 0) {
        this.setData({ currentStudent: students[0] })
        app.globalData.currentStudent = students[0]
        this.loadTodayCheckin(students[0].id)
      }
    }
  },

  async loadTodayCheckin(studentId) {
    const checkin = await CheckinAPI.today(studentId)
    this.setData({ todayCheckin: checkin })
  },

  onSelectStudent(e) {
    const id = e.currentTarget.dataset.id
    const student = this.data.students.find(s => s.id === id)
    if (student) {
      this.setData({ currentStudent: student })
      getApp().globalData.currentStudent = student
      this.loadTodayCheckin(id)
    }
  },

  onAddStudent() {
    wx.navigateTo({ url: '/pages/student/profile?mode=add' })
  },

  onDailyCheckin() {
    if (!this.data.currentStudent) return
    wx.navigateTo({
      url: `/pages/checkin/chat?studentId=${this.data.currentStudent.id}&studentName=${this.data.currentStudent.name}`,
    })
  },

  onCheckinHistory() {
    if (!this.data.currentStudent) return
    wx.navigateTo({
      url: `/pages/checkin/history?studentId=${this.data.currentStudent.id}`,
    })
  },

  onExamList() {
    if (!this.data.currentStudent) return
    wx.navigateTo({
      url: `/pages/exam/list?studentId=${this.data.currentStudent.id}`,
    })
  },

  onGuidance() {
    if (!this.data.currentStudent) return
    wx.navigateTo({
      url: `/pages/guidance/index?studentId=${this.data.currentStudent.id}`,
    })
  },
})
