import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { query } from '@angular/core/src/render3';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';
import { and } from '@angular/router/src/utils/collection';
import { isNull } from 'util';



@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

	baobab = 'aaaaaa';
	authLinkGenerated = false;
	linkToAuth = '';
	searchResult: any;
	searchPauseSplittedResult: any;

	private searchUrl =      			   'http://127.0.0.1:5000/search/';  // URL to web api
	private indexUrl =               'http://127.0.0.1:5000/add_to_index';
	private authLinkUrl =    				 'http://127.0.0.1:5000/authorize';
	private serverAuthLink = 				 'http://127.0.0.1:5000/oauth2callback';
	private searchPauseSplittedUrl = 'http://127.0.0.1:5000/search_pause_splitted/';


	constructor(
		private http: HttpClient,
		private router: Router
	) { }

	ngOnInit() {
	  let redirected_from_url = window.location.href;
	  if (!redirected_from_url.includes('?')) {
		return;
	  }
	  let parameters = redirected_from_url.split('?')[1].split('&').map(p => p.split('=')[0]);

	  if (parameters.indexOf('state') > -1 &&
		  parameters.indexOf('code') > -1 &&
		  parameters.indexOf('scope') > -1
		) {
		this.authorizeInServer(redirected_from_url);
		console.log('sent to authorization');
	  }
	}


	authorizeInServer(url: string) {
	  this.http.post<string>(this.serverAuthLink, {url: url})
		.subscribe(data => sessionStorage.setItem('public_key', data),
					error => console.log(error.message)                           );
	}

	getSearchResults(query) {
		let response = this.http.get<string[]>(this.searchUrl + query);
		response.subscribe(data => {
		  if (data != null) { this.searchResult = data; } else { this.searchResult = 'nothing found'; }});

		let response = this.http.get<string[]>(this.searchPauseSplittedUrl + query);
		response.subscribe(data => {
		  if (data != null) { this.searchPauseSplittedResult = data; } else { this.searchResult = 'nothing found'; }});
	}

  getAuthLink() {
		console.log('Authorizing');
		let response = this.http.get<string>(this.authLinkUrl);
		response.subscribe(data => {
				this.linkToAuth = data;
				this.goToLink(this.linkToAuth);
			}
		);
  }
  postVideoToIndex(videoId) {
	let response = this.http.post<string>(this.indexUrl,
		{
			videoId: videoId,
			public_key: sessionStorage.getItem('public_key')
		}
	);
	response.subscribe(
		m => this.baobab = m,
		error => this.baobab = error.message
	);
  }
  showQuery(val) {
	console.assert(val);
	this.baobab = val;
  }
  goToLink(url: string) {
	window.open(url, '_blank');
  }

  isAuthorizedToGoogle() {
	if (isNull(sessionStorage.getItem('public_key'))) {
		return false;
	} else {
		return true;
	}
  }
}
