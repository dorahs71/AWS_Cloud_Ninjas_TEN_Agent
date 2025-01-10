## 最新动手实验材料
我们已经构建了一份详细的动手实验材料，您可以从这个链接找到最新的内容，
https://catalog.us-east-1.prod.workshops.aws/workshops/5a9a9de1-6dd7-43b1-ba60-fc3792d99c40/zh-CN 。

## 目录如下
- 流程介绍
- 准备前置资源
- 部署 Astra 应用
    - 创建 EC2 服务器
    - 创建 CloudFront distribution
    - 登陆到 EC2 实例
    - 部署并启动 Astra 应用
    - 使用定制化的语音模型
- 体验语音对话及翻译
- 资源清理
- 总结
- 问题排查

## 内容简介
随着AI技术的快速发展，智能语音助手成为人机交互的重要方式。然而，传统语音助手开发需要大量时间和资源投入。Amazon Web Services 提供的一系列AI服务，如Amazon Bedrock、Transcribe 和 Amazon Polly，大大简化了开发过程。这些服务结合 [TEN（Transformative Extensions Network）Framework](https://doc.theten.ai/) 这样的多模态实时互动框架，使得即使没有深厚AI背景的开发者也能快速构建类似于 Astra 这样的强大的多模态交互Agent。

基于 Amazon Bedrock 构建端到端实时语音助手成为一个高效可行的方案，以满足企业对定制化语音服务的需求，同时利用云计算优势实现快速部署和弹性扩展。这种方案特别适合希望快速推出智能语音服务的企业和开发者。

本实验将使用 Amazon Bedrock、Transcribe、Polly 及 TEN 快速构建端到端实时语音助手，旨在为解决方案架构师、开发人员和 IT 专业人士提供动手实践。

### 预期收获
- 了解 Amazon Bedrock、Transcribe、Polly 服务
- 了解 Astra 语音助手的工作方式
- 体验基于 Astra 构建的对话场景及实时翻译场景

### 预计时长
1～2小时，取决于您对亚马逊云服务的熟悉度。

### 需要技术
- 了解 Ubuntu, NodeJS, NextJS, Docker 及 Docker Compose
- 了解基本的云服务，如 EC2，IAM，CloudFront，但不是必需的，我们在实验中提供了详细的操作步骤供您参考。

### 预估费用
实验费用主要由如下几部分构成：

- Amazon EC2 的成本：与运行时长有关，具体费用可以参考[这里](https://aws.amazon.
com/cn/ec2/pricing/)
- Bedrock LLM 调用费用: 与使用的 Input token 及 Output token有关，具体参考[这里]
(https://aws.amazon.com/bedrock/pricing/)
- Amazon Transcribe, 参考[这里](https://aws.amazon.com/transcribe/pricing/)
- Amazon Polly, 参考[这里](https://aws.amazon.com/polly/pricing/)
- Amazon CloudFront，参考[这里](https://aws.amazon.com/cloudfront/pricing/)
- Agora 使用成本，具体可以参考 Agora 官方的定价。

如果您在 2 小时内完成实验，预计费用应小于 $1。

我们建议您在完成实验后清理资源。