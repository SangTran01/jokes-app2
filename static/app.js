$(document).ready(function() {
  var auth = new auth0.WebAuth({
    domain: 'sangt.auth0.com',
    clientID: 'o6juNRGA8IdjX8MV8kLzmJ5ENEWzvO4P'
   });


    $('.btn-login').click(function(e) {
      e.preventDefault();
      auth.authorize({
        audience: 'https://' + 'sangt.auth0.com' + '/userinfo',
        scope: 'openid profile',
        responseType: 'code',
        redirectUri: 'http://localhost:5000/callback'
      });
    });

    $('.btn-logout').click(function(e) {
      e.preventDefault();
      window.location.href = '/logout';
    })
});  