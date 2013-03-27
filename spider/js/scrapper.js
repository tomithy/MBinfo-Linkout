/**
 * @fileoverview  Scrap info.
 */


var json_page, child_pages, att_pages;

var run = function() {
  var site_name = document.getElementById('site_name').value;
  var site_url = 'https://sites.google.com/feeds/content/mechanobio.info/' + site_name;
  var page_path = document.getElementById('page_path').value; // '/Home/Dynamic-Structures-in-Mechanosensing';

  json_page = SiteUtil.getPageByUrl(site_url, page_path);
  var page_id = SiteUtil.getId(json_page);

  child_pages = SiteUtil.getChildren(site_url, page_id, 'webpage');

  push_msg(child_pages.length + ' child pages of ' + SiteUtil.getTitle(json_page) + ' printed.');
  for (var page, i = 0; page = child_pages[i]; i++) {
    console.log(SiteUtil.getTitle(page) + ' ' + SiteUtil.getUrl(page))
  }

  att_pages = SiteUtil.getChildren(site_url, page_id, 'attachment');

  push_msg(att_pages.length + ' attachment of ' + SiteUtil.getTitle(json_page) + ' printed.');
  for (var page, i = 0; page = att_pages[i]; i++) {
    console.log(SiteUtil.getTitle(page) + ' ' + SiteUtil.getUrl(page))
  }

  return false;
};


var ele_msg = document.getElementById('msg');
var push_msg = function(msg) {
    var div_msg = document.createElement('div');
    div_msg.textContent = msg;
    ele_msg.appendChild(div_msg);
};



