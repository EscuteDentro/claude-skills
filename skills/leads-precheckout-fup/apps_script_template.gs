/**
 * Apps Script -- Captura de leads pré-checkout + follow-up (template genérico)
 *
 * COMO DEPLOYAR:
 * 1. Acesse script.google.com -> Novo projeto (standalone -- não precisa ser
 *    bound a nenhum documento)
 * 2. Cole este código, substituindo TODO_SHEET_ID e TODO_EMAIL_AVISO abaixo
 * 3. Implantações -> Nova implantação -> Tipo: App da Web
 *    - Executar como: Eu (sua conta Google)
 *    - Quem tem acesso: Qualquer pessoa
 * 4. Copie a URL gerada -- é ela que vai no APPS_SCRIPT_URL do modal da LP
 *
 * CRÍTICO -- leia antes de editar este código depois de já implantado:
 * a implantação do Web App é VERSIONADA e TRAVADA. Editar e salvar aqui NÃO
 * atualiza a URL /exec que já está em produção -- é preciso ir em
 * Implantar -> Gerenciar implantações -> editar a implantação ativa ->
 * Versão "Nova versão" -> Implantar. Sem esse passo, leads reais continuam
 * batendo no código antigo mesmo com este editor mostrando o fix salvo.
 * Depois de republicar, valide de verdade com um POST real contra a URL
 * /exec (é o que a LP faz) -- não confie só na aparência do editor salvo.
 */

var SHEET_ID  = 'TODO_SHEET_ID';
var SHEET_TAB = 'Leads';
var BANCO_MENSAGENS_TAB = 'Banco de Mensagens';
var EMAIL_AVISO = 'TODO_EMAIL_AVISO'; // quem recebe o e-mail diário de leads novos
var DIAS_CORTE_QUENTE_FRIO = 5; // ajuste pro seu ciclo de vendas

var EXPECTED_HEADERS = [
  'Timestamp', 'Nome', 'Status CRM', 'COMPROU', 'Obs', 'Duplicado',
  'E-mail', 'Telefone', 'Consentiu WA', 'Botão de origem',
  'UTM Source', 'UTM Medium', 'UTM Campaign', 'UTM Content',
  'Status', 'UTM Term', 'UTM Adset', 'Obs Duplicação'
];

// ── Endpoint principal ──────────────────────────────────────────────────

function doPost(e) {
  try {
    var data  = JSON.parse(e.postData.contents);
    var sheet = getOrCreateSheet();
    ensureHeaders(sheet);

    appendLeadRow(sheet, data);
    // Duplicado/Obs Duplicação NÃO são preenchidos aqui -- é responsabilidade
    // exclusiva da ferramenta de sinalização de duplicação (scripts Python
    // deste skill: plan_duplicado.py -> execute_duplicado.py), rodada sob
    // demanda ou agendada. Nunca duplicar essa lógica aqui: já causou bug
    // real (valor desatualizado sobrescrevendo a numeração correta) num
    // projeto que rodou essa versão antiga deste template.

    return ContentService.createTextOutput(JSON.stringify({ok: true}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ok: false, error: String(err)}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateSheet() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sheet = ss.getSheetByName(SHEET_TAB);
  if (!sheet) sheet = ss.insertSheet(SHEET_TAB);
  return sheet;
}

// Resolve nome de cabeçalho -> índice de coluna toda vez que roda. NUNCA usar
// posição fixa (tipo "coluna C") em nenhum lugar deste arquivo -- é isso que
// permite reordenar colunas na Sheet sem quebrar nada.
function getHeaderMap(sheet) {
  var lastCol = Math.max(sheet.getLastColumn(), 1);
  var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  var map = {};
  headers.forEach(function(h, i) { if (h) map[h] = i; });
  return map;
}

function ensureHeaders(sheet) {
  var map = getHeaderMap(sheet);
  var missing = EXPECTED_HEADERS.filter(function(h) { return !(h in map); });
  if (missing.length === 0) return;
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, EXPECTED_HEADERS.length).setValues([EXPECTED_HEADERS]);
    return;
  }
  var startCol = sheet.getLastColumn() + 1;
  sheet.getRange(1, startCol, 1, missing.length).setValues([missing]);
}

function appendLeadRow(sheet, data) {
  var hmap    = getHeaderMap(sheet);
  var numCols = sheet.getLastColumn();
  var row     = new Array(numCols).fill('');

  var fields = {
    'Timestamp':        data.timestamp    || new Date().toISOString(),
    'Nome':              data.nome         || '',
    'E-mail':             data.email        || '',
    'Telefone':           data.phone        || '',
    'Consentiu WA':       data.wa_consent   ? 'Sim' : 'Não',
    'Botão de origem':   data.origin_btn   || '',
    'UTM Source':         data.utm_source   || '',
    'UTM Medium':         data.utm_medium   || '',
    'UTM Campaign':       data.utm_campaign || '',
    'UTM Content':        data.utm_content  || '',
    'UTM Term':           data.utm_term     || '',
    'UTM Adset':          data.utm_adset    || '',
    'Status':             data.status       || 'lead_capturado',
  };

  Object.keys(fields).forEach(function(key) {
    if (key in hmap) row[hmap[key]] = fields[key];
  });

  sheet.appendRow(row);
}

// ── Ferramenta de WhatsApp (usada pelo e-mail diário) ───────────────────

function getMensagemWhatsApp(segmento) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sheet = ss.getSheetByName(BANCO_MENSAGENS_TAB);
  if (!sheet) return null;
  var values = sheet.getDataRange().getValues();
  var headers = values[0];
  var idx = {};
  headers.forEach(function(h, i) { idx[h] = i; });
  for (var i = 1; i < values.length; i++) {
    var row = values[i];
    var nome = String(row[idx['Nome do template']] || '').toLowerCase();
    var canal = row[idx['Canal']];
    if (canal === 'WhatsApp' && nome.indexOf(segmento) !== -1) {
      return row[idx['Texto']];
    }
  }
  return null;
}

function primeiroNome(nomeCompleto) {
  var primeiro = (nomeCompleto || '').trim().split(/\s+/)[0] || '';
  return primeiro.charAt(0).toUpperCase() + primeiro.slice(1).toLowerCase();
}

function linkWhatsApp(telefone, nomeCompleto, template) {
  if (!template) return null;
  var texto = template.replace('[Nome]', primeiroNome(nomeCompleto));
  var numero = String(telefone).replace(/\D/g, '');
  return 'https://wa.me/' + numero + '?text=' + encodeURIComponent(texto);
}

// ── Ferramenta de e-mail diário de novos leads ──────────────────────────

function emailLeadsDiarios() {
  var sheet = getOrCreateSheet();
  var hmap = getHeaderMap(sheet);
  var values = sheet.getDataRange().getValues();
  var agora = new Date();
  var novos = [];

  for (var i = 1; i < values.length; i++) {
    var row = values[i];
    var comprou = row[hmap['COMPROU']];
    if (comprou === 'Sim') continue;
    var ts = new Date(row[hmap['Timestamp']]);
    var horasDesde = (agora - ts) / 36e5;
    if (horasDesde <= 24) novos.push(row);
  }

  if (novos.length === 0) return; // só envia se tiver lead novo

  var linhas = novos.map(function(row) {
    var nome = row[hmap['Nome']];
    var telefone = row[hmap['Telefone']];
    var consentiu = row[hmap['Consentiu WA']];
    var timestamp = row[hmap['Timestamp']];

    if (consentiu !== 'Sim') {
      return '<p><b>' + nome + '</b> -- sem consentimento de WhatsApp, usar e-mail (Banco de Mensagens)</p>';
    }
    var template = getMensagemWhatsApp('quente'); // e-mail é diário -> lead novo é sempre "quente"
    var link = linkWhatsApp(telefone, nome, template);
    if (!link) {
      return '<p><b>' + nome + '</b> -- Banco de Mensagens sem template "quente" configurado</p>';
    }
    return '<p><b>' + nome + '</b> -- <a href="' + link + '">clique pra abrir o WhatsApp já com a mensagem pronta</a></p>';
  });

  var html = '<h3>Leads novos nas últimas 24h</h3>' + linhas.join('');
  MailApp.sendEmail({
    to: EMAIL_AVISO,
    subject: 'Leads pré-checkout novos (' + novos.length + ')',
    htmlBody: html,
  });
}

function criarAcionadorDiario() {
  // idempotente -- apaga o anterior antes de recriar, evita acionador duplicado
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === 'emailLeadsDiarios') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('emailLeadsDiarios').timeBased().everyDays(1).atHour(8).create();
}

// ── Teste local (rodar via Executar no editor, nunca substitui teste real) ─

function testeLocal() {
  var fakeEvent = {
    postData: {
      contents: JSON.stringify({
        nome: 'Teste Silva',
        email: 'teste@email.com',
        phone: '5511999990000',
        wa_consent: true,
        origin_btn: 'teste-manual',
        status: 'lead_capturado',
      })
    }
  };
  var resultado = doPost(fakeEvent);
  Logger.log(resultado.getContent());
}
