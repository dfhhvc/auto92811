export const metadata = {
  title: 'AutoIncome — AI驱动的被动收入机会聚合器',
  description:
    '自动追踪全网副业机会，AI智能分析、语义去重、个性化推荐。支持Web、桌面端和移动端。',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  )
}