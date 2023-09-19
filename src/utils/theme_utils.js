const theme = {
  rdf_dark: {
    // 背景颜色
    backgroundColor: '#161522',
    // 标题的文字颜色
    titleColor: '#fff',
    // 左上角logo的图标路径
    logoSrc: 'aqi.jpg',
    // 切换主题按钮的图片路径
    themeSrc: 'hgy.jpg',
    // 页面顶部的边框图片
    headerBorderSrc: 'header_border_dark.png'

  },
  vintage: {
    // 背景颜色
    backgroundColor: '#eeeeee',
    // 标题的文字颜色
    titleColor: '#000',
    // 左上角logo的图标路径
    logoSrc: 'aqi.jpg',
    // 切换主题按钮的图片路径
    themeSrc: 'hgy.jpg',
    // 页面顶部的边框图片
    headerBorderSrc: 'header_border_light.png'
  }
}

export function getThemeValue (themeName) {
  return theme[themeName]
}
