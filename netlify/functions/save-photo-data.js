// Netlify Function: 接收合并后的摄影数据，通过 GitHub API 提交到 photography-data.json
// 需要环境变量: GITHUB_TOKEN, GITHUB_REPO (格式: owner/repo)

exports.handler = async (event) => {
  // 仅接受 POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  // 读取请求体（无需在服务端再次验证 Identity token——客户端已验）
  let body;
  try {
    body = JSON.parse(event.body);
  } catch (e) {
    return { statusCode: 400, body: 'Bad Request: invalid JSON' };
  }

  const { data, message, token } = body;

  // 至少要有 token 表示已登录
  if (!token) {
    return { statusCode: 401, body: 'Unauthorized: missing token' };
  }

  if (!Array.isArray(data)) {
    return { statusCode: 400, body: 'Bad Request: data must be an array' };
  }

  const githubToken = process.env.GITHUB_TOKEN;
  const repo = process.env.GITHUB_REPO || 'OVISTGLLD/My-first-agent-project';
  const filePath = 'photography-data.json';

  if (!githubToken) {
    return { statusCode: 500, body: 'Server Error: GITHUB_TOKEN not configured' };
  }

  const apiBase = `https://api.github.com/repos/${repo}/contents/${filePath}`;

  try {
    // 1. 获取当前文件 SHA
    const getRes = await fetch(apiBase, {
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: 'application/vnd.github.v3+json',
      },
    });
    if (!getRes.ok) {
      return { statusCode: 502, body: `GitHub API error (get): ${getRes.status} ${await getRes.text()}` };
    }
    const fileInfo = await getRes.json();
    const sha = fileInfo.sha;

    // 2. 生成新的 JSON 内容
    const newContent = JSON.stringify(data, null, 2) + '\n';
    const encoded = Buffer.from(newContent).toString('base64');

    // 3. PUT 更新文件
    const commitMsg = message || '更新 photography-data.json';
    const putRes = await fetch(apiBase, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: commitMsg,
        content: encoded,
        sha: sha,
      }),
    });

    if (!putRes.ok) {
      return { statusCode: 502, body: `GitHub API error (put): ${putRes.status} ${await putRes.text()}` };
    }

    const putResult = await putRes.json();
    return {
      statusCode: 200,
      body: JSON.stringify({
        ok: true,
        commit: putResult.commit?.sha?.slice(0, 7) || 'ok',
        message: '数据已保存，Netlify 将自动重新部署',
      }),
    };
  } catch (err) {
    return { statusCode: 500, body: `Server Error: ${err.message}` };
  }
};
