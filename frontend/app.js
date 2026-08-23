const API_URL="http://127.0.0.1:8001/agent";
const HEALTH_URL="http://127.0.0.1:8001/health";
const chat=document.getElementById("chat");
const form=document.getElementById("chatForm");
const input=document.getElementById("message");
const requestCount=document.getElementById("requestCount");
const lastAction=document.getElementById("lastAction");
const apiStatus=document.getElementById("apiStatus");
let requests=0;

function esc(v){return String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}

function invoiceTable(result){
  if(!result||!Array.isArray(result.invoices)||!result.invoices.length)return "";
  const rows=result.invoices.map(i=>`<tr><td>${esc(i.id)}</td><td>${esc(i.customer)}</td><td>${Number(i.amount).toFixed(2)}</td><td>${esc(i.status)}</td></tr>`).join("");
  return `<div class="table-wrap"><table><thead><tr><th>Invoice</th><th>Customer</th><th>Amount</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function addMessage(text,role,tool=null,result=null){
  const row=document.createElement("div");
  row.className=`message ${role}`;
  row.innerHTML=`${role==="assistant"?'<div class="avatar">OD</div>':""}<div class="message-content">${role==="assistant"?'<span class="sender">OpsDesk</span>':""}<div class="bubble">${esc(text)}${tool==="search_invoices"?invoiceTable(result):""}</div>${tool?`<div class="tool">${esc(tool)}</div>`:""}</div>`;
  chat.appendChild(row);
  chat.scrollTop=chat.scrollHeight;
}

function updateActivity(tool,result){
  requests++;
  requestCount.textContent=requests;
  const detail=tool==="search_invoices"
    ? `${result?.count ?? 0} matching invoice(s) returned`
    : `${result?.count ?? 0} invoice(s) · total ${Number(result?.total_amount ?? 0).toFixed(2)}`;
  lastAction.classList.remove("empty");
  lastAction.innerHTML=`<span class="action-icon">↗</span><div><strong>${esc(tool)}</strong><p>${esc(detail)}</p></div>`;
}

async function checkHealth(){
  try{
    const r=await fetch(HEALTH_URL);
    if(!r.ok)throw new Error();
    apiStatus.className="api-status online";
    apiStatus.innerHTML="<span></span> API connected";
  }catch{
    apiStatus.className="api-status offline";
    apiStatus.innerHTML="<span></span> API offline";
  }
}

async function askAgent(message){
  addMessage(message,"user");
  addMessage("Working on it…","assistant");
  const pending=chat.lastElementChild;
  try{
    const r=await fetch(API_URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});
    if(!r.ok)throw new Error(`API ${r.status}`);
    const data=await r.json();
    pending.remove();
    addMessage(data.response,"assistant",data.selected_tool,data.tool_result);
    updateActivity(data.selected_tool,data.tool_result);
  }catch(e){
    pending.remove();
    addMessage(`Could not complete the request (${e.message}). Check that the local API is running.`,"assistant");
  }
}

form.addEventListener("submit",e=>{e.preventDefault();const v=input.value.trim();if(!v)return;input.value="";askAgent(v)});
document.querySelectorAll("[data-prompt]").forEach(b=>b.addEventListener("click",()=>askAgent(b.dataset.prompt)));
checkHealth();