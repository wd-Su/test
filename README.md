# CI/CD 实战 · 发布阅读进度页

你负责维护团队的阅读进度页。每次提交 PR，GitHub Actions 都要跑测试并构建页面。合入 `main` 后，再用通过检查的构建产物更新 GitHub Pages。你会亲手创建 **`.github/workflows/pipeline.yml`**，先写 CI，再加 CD。

## 0. 跑通本地基线

需要 Git 和 Python 3.12。项目只用 Python 标准库。

```powershell
Set-Location 'E:\learning\daily\计算机\cicd'
python -m unittest discover -s tests -v
python build.py
Invoke-Item .\dist\index.html
```

预期看到 **5 个测试通过**，网页显示 **40%（已读 4 / 10 本）**。`reading.json` 是页面数据，`reading.py` 计算进度，`build.py` 根据模板生成 `dist/index.html`。

在 GitHub 创建一个空仓库。创建时将 README、.gitignore 和许可证的初始化选项留空，本地已经有首个提交。用 GitHub Free 跟练 Pages 时，选择公开仓库。复制仓库的 HTTPS 地址，替换下面的示例地址，再执行。 [推送本地仓库](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) · [Pages 可用范围](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

```powershell
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

## 1. 写 CI · 提交时自动检查

CI（持续集成）在代码变动时自动验证测试和构建。新建 `.github/workflows/pipeline.yml`，设计一个测试与构建的 job。

- 触发时机是推送到 `main`，以及对 `main` 发起或更新 PR。
- 在 GitHub 托管的 Linux runner 上检出代码，准备 Python 3.12。
- 依次运行本地用过的测试与构建命令。测试失败时，后面的构建步骤应被跳过。

**验收**　提交工作流并推送到 `main`。打开 GitHub 的 **Actions**，在这次运行的日志里找到 5 个测试通过和 `Built dist/index.html`。

```powershell
git add .github/workflows/pipeline.yml
git commit -m "Add CI workflow"
git push
```

<details>
<summary>卡住时展开 CI 提示</summary>

- 用 `on` 声明事件，给 `push` 和 `pull_request` 各加分支过滤。PR 的分支过滤匹配目标分支。 [事件与分支过滤](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpull_requestpull_request_targetbranchesbranches-ignore)
- 从 `jobs`、`runs-on` 和 `steps` 开始。用 `actions/checkout` 和 `actions/setup-python` 准备环境，用 `run` 执行命令。检出代码需要 `contents: read` 权限。 [Python 工作流](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)

</details>

## 2. 写 CD · 把构建结果发布出去

这里的 CD 指持续部署，通过检查的主分支改动会自动上线。在 GitHub 仓库的 **Settings → Pages → Build and deployment** 中，把 **Source** 设为 **GitHub Actions**。接着修改同一份 `pipeline.yml`。 [配置 Pages 的发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

- 当事件是推送到 `main` 时，在构建成功后，把 `dist/` 上传为 Pages artifact，也就是这次工作流生成的站点文件。
- 增加一个部署 job。它必须等待测试与构建的 job 成功，并且只在推送到 `main` 时运行。在 `github-pages` 环境中部署刚才上传的 artifact。
- 让 GitHub 在部署记录里显示 Pages URL。

**验收**　提交并推送。等 Actions 中两个 job 都成功，点击部署记录里的 URL，确认线上也显示 **40%**。

<details>
<summary>卡住时展开 CD 提示</summary>

- 构建 job 用 `actions/upload-pages-artifact` 打包 `dist/`，部署 job 用 `actions/deploy-pages` 发布。同一次工作流里，两个 job 通过 artifact 传递文件。 [Pages artifact 与部署](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- 用 `needs` 写 job 依赖。用 `if` 判断事件和分支，可查 `github.event_name` 和 `github.ref`。`main` 的完整 ref 是 `refs/heads/main`。 [工作流语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) · [github 上下文](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#github-context)
- 部署 job 需要 `pages: write` 与 `id-token: write`。给部署步骤一个 `id`，让 `environment.url` 引用该步骤的 `page_url` 输出。 [部署参数与输出](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages#deploying-github-pages-artifacts)

</details>

## 3. 演练 · 从红灯到上线

1. 从 `main` 新建分支 `git switch -c practice/reading-update`。把 `reading.json` 的 `completed` 从 4 改成 6，文案中的本数也改成 6。为了制造一次回归，把 `reading.py` 中百分比公式的除数 `goal` 临时改成 `(goal + 1)`。
2. 提交这两个文件，用 `git push -u origin practice/reading-update` 推送。在 GitHub 开一个目标为 `main` 的 PR。等 CI 跑完，在日志里找到 `test_partial_progress` 的失败。此时线上仍显示 **40%**。
3. 恢复正确的公式，保留阅读数据的更新。在同一分支提交并推送。看到 PR 检查转绿、部署 job 显示跳过后，再合并 PR。
4. 在 **Actions** 里找到合并后由 `main` 推送触发的那次运行。等部署成功后刷新 Pages，核对 **60%（已读 6 / 10 本）**。

[如何创建 PR](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)

演练结束后，试着指着日志回答两个问题。测试失败后，哪个步骤被跳过了？部署 job 用哪个产物发布了 60% 的页面？
