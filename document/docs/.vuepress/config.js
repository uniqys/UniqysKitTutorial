module.exports = {
  base: '/UniqysKitSample/',
  title: 'Uniqys Kit Simple Samples',
  dest: '../docs',
  markdown: {
    lineNumbers: true
  },
  themeConfig: {
    nav: [
        { text: 'Uniqys Kit', link: 'https://uniqys.net/ja' },
        { text: 'GitHub', link: 'https://github.com/uniqys' },
    ],
    sidebar: [
      {
        title: 'messages',
        collapsable: false,
        children: [
          '/messages/step-1-js/',
          '/messages/step-2-js/',
          '/messages/step-1-python/',
          '/messages/step-2-python/',
        ]
      },
      {
        title: 'sushi',
        collapsable: false,
        children: [
          '/sushi/step-1/',
          '/sushi/step-2-js/',
          '/sushi/step-2-python/',
        ]
      },
      '/qa/',
    ]
  }
}