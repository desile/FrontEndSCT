<template>
    <div class="app">
            <v-app id="example-1" toolbar footer>
                <v-navigation-drawer
                        persistent
                        v-model="drawer"
                        light
                        enable-resize-watcher>
                    <v-list dense>
                        <v-list-tile @click="$router.push(item.url)" v-for="item in menuItems" :key="item.url">

                            <v-list-tile-action>
                                <v-icon>{{item.icon}}</v-icon>
                            </v-list-tile-action>
                            <v-list-tile-content>
                                <v-list-tile-title>
                                    {{item.label}}
                                </v-list-tile-title>
                            </v-list-tile-content>

                        </v-list-tile>
                    </v-list>
                </v-navigation-drawer>
                <v-toolbar class="indigo" dark fixed>
                    <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
                    <v-toolbar-title>Система семантической оценки ответов</v-toolbar-title>
                </v-toolbar>
                <main>
                    <v-container fluid>
                        <div class="page">  <!-- Надо ли этот див -->
                            <router-view></router-view>
                        </div>
                    </v-container>
                </main>
                <v-footer class="indigo">
                    <span class="white--text">&copy; 2017</span>
                </v-footer>
            </v-app>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                drawer: true,
                menuItems: [
                    {url: '/', icon: 'home', label: 'Главная'},
                    {url: '/wizard', icon: 'school', label: 'Wizard'},
                    {url: '/questions', icon: 'school', label: 'Список вопросов'},
                    {url: '/add_answer', icon: 'class', label: 'Управление ответами'},
                    {url: '/check_answer', icon: 'class', label: 'Проверка ответа'},
                ]
            }
        },
        name: 'app'
    }
</script>
