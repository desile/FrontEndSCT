import Vue from 'vue'
import Router from 'vue-router'
import AddAnswerPage from '../pages/AddAnswerPage.vue'
import HomePage from '../pages/HomePage.vue'
import QuestionsPage from '../pages/QuestionsPage.vue'
import CheckAnswer from '../pages/CheckAnswerPage.vue'
import WizardPage from '../pages/WizardPage.vue'

Vue.use(Router);

export default new Router({
    routes: [
        {
            path: '/add_answer',
            name: 'addAnswerPage',
            component: AddAnswerPage
        },
        {
            path: '/questions',
            name: 'addQuestion',
            component: QuestionsPage
        },
        {
            path: '/check_answer',
            name: 'checkAnswer',
            component: CheckAnswer
        },
        {
            path: '/',
            name: 'homePage',
            component: HomePage
        },
        {
            path: '/wizard',
            name: 'wizard',
            component: WizardPage
        }
    ]
})