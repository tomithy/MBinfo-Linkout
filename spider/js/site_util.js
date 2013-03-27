/**
 * @fileoverview Walk a Google Site.
 *
 * This use Google Site API,
 * @see {@link https://developers.google.com/google-apps/sites/docs/1.0/reference}
 * for more info.
 */

var SiteUtil = {};


/**
 * Given a path return a page in JSON
 * @param {string} site_url https://sites.google.com/a/mechanobio.info/mbinfo
 * @param {string} path /Home
 * @param {Object} page data in JSON format
 */
SiteUtil.getPageByUrl = function(site_url, path) {

  var result;

  $.ajax({
    url: site_url,
    data: {
      alt: 'json',
      path: path
    },
    async: false,
    success: function(data) {
      result = data;
    }
  });

  return result.feed.entry[0];
};


/**
 *
 * @param {string} site_url
 * @param {string} page_id
 * @param {string} type webpage, attachment
 * @return {Array} list of pages
 */
SiteUtil.getChildren = function(site_url, page_id, type) {
  var result;

  $.ajax({
    url: site_url,
    data: {
      alt: 'json',
      parent: page_id,
      kind: type
    },
    async: false,
    success: function(data) {
      result = data;
    }
  });

  return result.feed.entry || [];
};


/**
 *
 * @param {Object} page page in JSON
 * @reutrn {string} page id
 */
SiteUtil.getId = function(page) {
  return page.id.$t.match(/\d+$/)[0];
};


/**
 *
 * @param {Object} page page in JSON
 * @reutrn {string} page title
 */
SiteUtil.getTitle = function(page) {
  return page.title.$t;
};


/**
 *
 * @param {Object} page page in JSON
 * @reutrn {string} page url
 */
SiteUtil.getUrl = function(page) {
  for (var link, i = 0; link = page.link[i]; i++) {
    if (link.rel == 'alternate') {
      return link.href;
    }
  }
};