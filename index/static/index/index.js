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

Vue.component('thread', {
	props: ['thread'],
	// data: function () {
	// 	return {}
	// },
	template: `
<div class="card mb-3">
	<div class="row no-gutters">
		<div class="card-header col-md-12">
			<p style="margin: 0 0 0 15px;">{{ thread.posterName }} &bull; {{ thread.datetime }} &bull; №{{ thread.postId }}
				<a style="float: right; margin-right: 15px;" href="#" class="card-link">Открыть</a></p>
		</div>
		<div class="col-md-4">
			<!--suppress RequiredAttributes -->
			<img :src="thread.imagePreviewUrl"
				 class="card-img"
				 alt="OP-post image"
				 style="height: 100%"> <!-- TODO: image -->
		</div>
		<div class="col-md-8">
			<div class="card-body">
				<h5 class="card-title">{{ thread.name }}</h5>
				<p class="card-text">{{ thread.text }}</p>
				<p class="card-text">
					<small class="text-muted">Пропущено {{ thread.postsCount }} постов, из них {{ thread.postsWithFilesCount }} с файлами</small>
				</p>
			</div>
		</div>
	</div>
</div>`
});

const app = new Vue({
	el: '#app',
	data: {
		threadsList: [
			{
				posterName: 'Анонимус',
				datetime: '23/03/19 Суб 23:03:44',
				postId: 2281337,
				imagePreviewUrl: 'https://placeimg.com/640/480/any/sepia',
				name: 'Первый тред!',
				text: 'Какой-то там таки текст, да.',
				postsCount: 200,
				postsWithFilesCount: 50
			},
			{
				posterName: 'Пионер',
				datetime: '23/03/19 Суб 23:43:44',
				postId: 22874949849,
				imagePreviewUrl: 'https://placeimg.com/640/480/any/sepia',
				name: 'Второй тредик...',
				text: 'Здесь текст, естесственно,\nдругой.',
				postsCount: 200,
				postsWithFilesCount: 50
			}
		],
	},
	created: function () {
		console.info('created!', this);
	}
});
