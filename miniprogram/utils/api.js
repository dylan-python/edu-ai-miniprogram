/**
 * API 服务层
 * 封装后端接口调用 — WeChat Mini Program CommonJS
 */
const BASE_URL = () => {
  const app = getApp()
  return app.globalData.baseUrl || 'https://edu-ai-miniprogram-production.up.railway.app'
}

function request(path, options = {}) {
  const { method = 'GET', data, loading = true } = options
  if (loading) wx.showLoading({ title: '加载中...', mask: true })
  return new Promise((resolve) => {
    wx.request({
      url: `${BASE_URL()}${path}`,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (loading) wx.hideLoading()
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)
        else { wx.showToast({ title: `请求失败(${res.statusCode})`, icon: 'none' }); resolve(null) }
      },
      fail: () => {
        if (loading) wx.hideLoading()
        wx.showToast({ title: '网络异常，请检查后端服务', icon: 'none' })
        resolve(null)
      },
    })
  })
}

const StudentAPI = {
  list: () => request('/api/students'),
  get: (id) => request(`/api/students/${id}`),
  create: (data) => request('/api/students', { method: 'POST', data }),
  update: (id, data) => request(`/api/students/${id}`, { method: 'PUT', data }),
  delete: (id) => request(`/api/students/${id}`, { method: 'DELETE' }),
}

const CheckinAPI = {
  create: (data) => request('/api/checkin/', { method: 'POST', data }),
  history: (studentId, days = 30) => request(`/api/checkin/history/${studentId}?days=${days}`),
  today: (studentId) => request(`/api/checkin/today/${studentId}`),
  aiChat: (studentId, message, contextType = 'checkin', sessionData = {}) =>
    request('/api/checkin/ai-chat', {
      method: 'POST',
      data: { student_id: studentId, message, context_type: contextType, session_data: sessionData },
    }),
}

const ExamAPI = {
  create: (data) => request('/api/exams/', { method: 'POST', data }),
  list: (studentId) => request(`/api/exams/student/${studentId}`),
  get: (examId) => request(`/api/exams/${examId}`),
}

const GuidanceAPI = {
  list: (studentId) => request(`/api/guidance/${studentId}`),
  create: (data) => request('/api/guidance/', { method: 'POST', data }),
  aiGenerate: (studentId) => request(`/api/guidance/ai-generate/${studentId}`, { method: 'POST' }),
}

module.exports = { StudentAPI, CheckinAPI, ExamAPI, GuidanceAPI }
