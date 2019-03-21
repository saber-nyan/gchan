/******************************************************************************
 * Copyright 2019 saber-nyan                                                  *
 *                                                                            *
 * Licensed under the Apache License, Version 2.0 (the "License");            *
 * you may not use this file except in compliance with the License.           *
 * You may obtain a copy of the License at                                    *
 *                                                                            *
 *     http://www.apache.org/licenses/LICENSE-2.0                             *
 *                                                                            *
 * Unless required by applicable law or agreed to in writing, software        *
 * distributed under the License is distributed on an "AS IS" BASIS,          *
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   *
 * See the License for the specific language governing permissions and        *
 * limitations under the License.                                             *
 ******************************************************************************/

'use strict';
Vue.component('post', {
	props: ['post', 'id'],
	data: function () {
		return {
			isActive: true
		}
	},
	template: `
<div @click="isActive = !isActive" :class="{ 'btn-warning': !isActive }" class="media text-muted pt-3">
	<svg class="bd-placeholder-img mr-2 rounded" width="32" height="32" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" focusable="false" role="img" aria-label="Placeholder: 32x32"><title>Placeholder</title><rect width="100%" height="100%" fill="#007bff"></rect><text x="50%" y="50%" fill="#007bff" dy=".3em">32x32</text></svg>
	<p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
		<strong class="d-block text-gray-dark">#{{ id }} - {{ post.username }}</strong>
<!--		<span v-html="post.text"></span>-->
		{{ post.text }}
	</p>
</div>`
});

const app = new Vue({
	el: '#app',
	data: {
		postsList: [
			{username: 'Анонимус', text: 'Что-то про воду'},
			{username: 'Пионер', text: 'Что-то про CENSORED'},
			{username: 'Анонимус', text: 'Что-то на\nмного\nстрочек!'}
		],
		nextPost: {
			text: '',
			username: ''
		}
	},
	methods: {
		addNewPost: function () {
			this.postsList.push({
				username: this.nextPost.username,
				text: this.nextPost.text
			});
			this.nextPost.text = '';
			this.nextPost.username = '';
		}
	},
	created: function () {
		console.info('created!', this);
	}
});
