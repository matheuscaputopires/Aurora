"use strict";

function Details(messages, documentElement) {
  const t0 = performance.now();
  const c = document.createDocumentFragment();
  for (let e of messages)
  {
    c.appendChild(makeMessage(e));
  }
  const perf = `Details total: ${(performance.now() - t0).toFixed(3)} ms`
  console.log(perf);
  // uncomment to show in UI
  /*
  var f = document.createElement("div");
  f.textContent = perf;
  c.insertBefore(f, c.firstChild)
  */
  documentElement.appendChild(c);
}

function makeMessage(msg)
{
  if (typeof msg.element !== 'undefined')
    return makeMessageJson(msg);
  else if (typeof msg === 'string') //HTML message
    return makeMessageHtml(msg);

  if (Array.isArray(msg))
  {
    const c = document.createDocumentFragment();
    msg.forEach(function (it) { c.appendChild(makeMessage(it)); })
    return c;
  }
  return makeMessageGP(msg);
}

function makeMessageGP(msg)
{
  const ret = document.createElement("pre");
  if (msg.Type === 0) return ret.textContent = msg.Text, ret;

  //handle warnings and errors
  const cn = (50 === msg.Type) ? "warning" : "error";
  ret.className = cn;

  function fn_pre(txt) {
    const span = document.createElement("span");
    span.className = cn + "-link";
    span.textContent = txt;
    return span;
  }

  function fn_icon() {
    const icon = document.createElement("span");
    icon.className = cn + "-icon";
    return icon;
  }

  function fn_link(txt, id) {
    const a = document.createElement("a");
    a.href = "javascript:void(0);";
    a.onclick = async function () {
      await messagesAsync.launchHelp(this.id);
      return false;
    }
    a.className = cn + "-link";
    a.style.textDecoration = "underline";
    a.textContent = txt;
    a.id = id;
    return a;
  }

  const regex = /(WARNING|ERROR) +(\d*)( ?:? ?:)/gm;
  let m = [...msg.Text.matchAll(regex)];
  if (m.length > 0) {
    //console.log(m);
    var pos = 0;
    for (let x of m) {
      const start = x.index;
      const end = start + x[0].length;
      if (pos < start)
        ret.appendChild(fn_pre(msg.Text.substring(pos, start)));
      var code = parseInt(x[2]);
      if (isNaN(code)) code = msg.ErrorCode
      ret.appendChild(fn_icon());
      ret.appendChild(fn_link(`${x[1]} ${x[2]}:`, code));
      pos = end;
    }
    //add tail
    if (pos < msg.Text.length)
      ret.appendChild(fn_pre(msg.Text.substring(pos, msg.Text.length)));
  } else {
    ret.appendChild(fn_icon());
    ret.appendChild(fn_pre(msg.Text));
  }
  return ret;
}

function makeMessageHtml(msg)
{
  var ret = document.createElement("div");
  ret.innerHTML = msg;
  return ret;
}

function makeMessageJson(msg)
{
  switch (msg.element.toLowerCase()) {
    case "table":
      return Table(msg.data, msg.elementProps);
    case "image":
      return Image(msg.data, msg.elementProps);
    case "content":
      return Content(msg.data, msg.elementProps);
    case "h1":
    case "h2":
    case "h3":
    case "h4":
    case "h5":
    case "h6":
    case "h7":
      return Header(msg.data, msg.element.toLowerCase());
    case "sectiontitle":
      return Header(msg.data, "h2");
    case "orderedlist":
      return BulletList(msg.data, msg.elementProps, "ol");
    case "unorderedlist":
      return BulletList(msg.data, msg.elementProps, "ul");
    case "p":
      return Paragraph(msg.data);
    case "hyperlink":
      return Hyperlink(msg.data, msg.link? msg.link: msg.data);
    case "sub":
    case "subscript":
      return Subscript(msg.data);
    case "sup":
    case "superscript":
      return Superscript(msg.data);
    case "accordion":
      return Accordion(msg.data, msg.elementProps)
    default:
      return Paragraph(msg.data, msg.elementProps);
  }
}

function Content(data, config) {
  let content = document.createElement("div");
  content.id = config && config.id;
  content.className = config && config.className;
  content.style.cssText = config && config.style;
  processContent(content, data);
  return content;
}

function Image(data, config) {
  var image = document.createElement("img");
  image.id = uuidv4();
  image.className = config && config.className;
  image.style.cssText = config && config.style;
  image.src = data;
  return image;
}

function Paragraph(data, config) {
  var paragraph = document.createElement("p");
  paragraph.id = config && config.id;
  paragraph.className = config && config.className;
  paragraph.style.cssText = config && config.style;
  processContent(paragraph, data)
  return paragraph;
}

function Table(data, config) {
  // const div = document.createElement("div");
  // div.className = 'table-wrapper';
  const table = document.createElement("table");
  table.id = config && config.id;
  table.className = `${config && config.className} table `.concat(config && config.striped ? "table-striped" : "");;
  table.style.cssText = config && config.style;

  let header = null;
  if(config && config.noHeader){
    header = [];
  }else{
    header = (config && config.header) || data.splice(0, 1)[0];
  }

  table.appendChild(tableHeader(header, config));
  tableRows(table, data, config);

  // NOTE remove the thead and tbody wrapper, otherwise, the header row will not be able to merge with the below rows
  // `<thead>
  //     ${tableHeader(header, config)}
  // </thead>
  // <tbody>
  //     ${tablerows(data, config).join('')}
  // </tbody>`;
    
  const c = document.createDocumentFragment();
  const title = config && config.title;
  if(title){
    c.appendChild(Header(title, "h5"));
  }
  c.appendChild(table);
  const footNote = config && config.footnote;
  if(footNote){
    footNote.forEach(function (note) { c.appendChild(Header(note, "h7")); })
  }
  return c;
}


function setTableCellProp(cell, prop){
  if(Number.isInteger(prop.rowspan)){
    cell.setAttribute("rowspan", prop.rowspan);
  }
  if(Number.isInteger(prop.colspan)){
    cell.setAttribute("colspan", prop.colspan);
  }

  let style = "";
  if(typeof prop["font-weight"] !== 'undefined'){
    style += `font-weight:${prop['font-weight']}; `;
  }
  if(typeof prop["text-align"] !== 'undefined'){
    style += `text-align:${prop['text-align']}; `;
  }

  if(style.length > 0){
    cell.style.cssText += style;
  }
}

function tableCell(data, config, isHeaderCell = false) {
  let classNames = [`align-${(config && config.align ? config.align : "left")}`, `cell-${(config && config.wrap ? "wrap" : "no-wrap")}`];
  let cell = null;
  if (isHeaderCell) {
    cell = document.createElement("th");
  } else {
    cell = document.createElement("td");
  }
  cell.className = classNames.join(" ");
  if (data !== null && typeof data === "object" && typeof data.data !== 'undefined') {
    if (typeof data.prop !== 'undefined') {
      setTableCellProp(cell, data.prop);
    }
    processContent(cell, data.data);
  } else {
    processContent(cell, data);
  }
  return cell;
}

function tableHeader(headerData, config){
  let tr = document.createElement("tr");
  headerData.forEach((header, ind) => {
    tr.appendChild(tableCell(header, config[ind], true));
  });
  return tr;
}

function tableRows(container, rowdata, config){
  const classStr = `${ config && config.rowClass || ""} ${ (config.underline && config.underline.indexOf(ind) > -1) ? "row-underline": "" } style=${config && config.rowStyle}`;
  rowdata.forEach((row) => {
    let tr = document.createElement("tr");
    tr.className = classStr;
    row.forEach((cell, ind) => {
      tr.appendChild(tableCell(cell, config[ind], false));
    });
    container.appendChild(tr);
  });
}

function Header(content, level="h1"){
  level = level.toLowerCase();
  const supportedLevels = ["h1", "h2", "h3", "h4", "h5", "h6", "h7"];
  if(supportedLevels.indexOf(level) < 0){
    return "";
  }
  const header = document.createElement("div");
  const ele = document.createElement(level);
  processContent(ele, content);
  header.appendChild(ele);
  return header;
}

function BulletList(data, config, lType){
  const bulletList = document.createElement(lType);
  bulletList.id = config && config.id;
  bulletList.style.cssText = config && config.style;
  data.forEach((content) => {
    let listItem = document.createElement("li");
    processContent(listItem, content);
    bulletList.appendChild(listItem);
  });
  return bulletList;
}

function Hyperlink(text, link){
  let ele = document.createElement("a");
  ele.href = link;
  ele.innerText = String(text);
  ele.target = "_blank";
  return ele;
}

function Superscript(text){
  let ele = document.createElement("sup");
  ele.innerText = String(text);
  return ele;
}

function Subscript(text){
  let ele = document.createElement("sub");
  ele.innerText = String(text);
  return ele;
}

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function Accordion(elements, config) {
  const container = document.createElement("div");
  
  let uniqueID = uuidv4();
  let titleLevel = "5";
  if(config && config.level){
    if(["1", "2", "3", "4", "5", "6"].indexOf(String(config.level)) >= 0){
      titleLevel = String(config.level);
    }
  }
  let accordionTitle = document.createElement(`h${titleLevel}`);
  accordionTitle.innerHTML = `<div class="image"></div>${config.title ?? ""}`;
  accordionTitle.id = `${uniqueID}`;
  accordionTitle.active = false;
  accordionTitle.onclick = onClickAccordionTitle;
  let accordionBody = document.createElement("div");
  accordionBody.appendChild(makeMessage(elements));
  if(Array.isArray(elements)){
    if(elements[0].element.toLowerCase() === "table"){
      accordionBody.style.paddingTop = "0";
    }
  }
  accordionBody.className = "accordion-body";
  accordionBody.id = `accordion-body${uniqueID}`;
  let expand = false;
  if(config && config.expand === true){
    expand = true;
  }
  if(expand){
    accordionTitle.className = "accordion-title open";
    accordionBody.style.display = "block";
  }else{
    accordionTitle.className = "accordion-title";
    accordionBody.style.display = "none";
  }
  container.appendChild(accordionTitle);
  container.appendChild(accordionBody);
  return container;
}

function onClickAccordionTitle(event) {
  const accordionTitle = event?.currentTarget;
  const id = accordionTitle.id;
  const accordionBody = document.querySelector(`#accordion-body${id}`);
  if(accordionBody !== undefined) {
    const display = accordionBody.style.display;
    if (display === "none") {
      accordionBody.style.display = "block";
      accordionTitle.className = "accordion-title open";
    } else {
      accordionBody.style.display = "none";
      accordionTitle.className = "accordion-title";
    }
  }
}

function processContent(container, data){
  if(typeof data === 'string'){
    container.innerText = data;
  }else if(Array.isArray(data)){
    data.forEach(function(component){
      try{
        if(typeof component === "object" && typeof component.element !== 'undefined'){
          switch(component.element.toLowerCase()){
            case "hyperlink":
            {
              container.appendChild(Hyperlink(component.data, component.link? component.link: component.data));
              break;
            }
            case "sup":
            case "superscript":
            {
              container.appendChild(Superscript(component.data));
              break;
            }
            case "sub":
            case "subscript":
            {
              container.appendChild(Subscript(component.data));
              break;
            }
            case "break":
            {
              container.appendChild(document.createElement("br"));
              break;
            }
            default:
            {
              let ele = document.createTextNode(String(component.data));
              container.appendChild(ele);
            }
          }
        }else{
          let span = document.createTextNode(String(component));
          span.innerText = String(component);
          container.appendChild(span);
        }
      }catch(err){
        return;
      }
    });
  }else{
    container.innerText = String(data);
  }
}