import Vue from 'vue';

const state = {
    question: '',
    questions: [], //question.text, question.id
    questionTableHeaders: [
        {text: 'Вопрос', value: 'question', align: 'left'},
        {text: 'Количество ответов', value: 'answerCount'}
    ]
};

const actions = {
    addQuestion({commit}) {
        Vue.http.post('http://localhost:8000/questions', {question: state.question}).then(response => {
            if (response.body) {
                //state.questions = response.body
            }
            commit('clear_question_field');
            commit('load_questions')
        });
    },
    addText({commit}, text) {
        commit('update_question', text)
    }
};

const mutations = {
    clear_question_field(state) {
        state.question = ''
    },
    update_question(state, update) {
        state.question = update
    },
    load_questions(state) {
        Vue.http.get('http://localhost:8000/questions').then(response => {
            if (response.body) {
                state.questions = response.body;
                console.log(state.questions)
            }
        });
    }
};

const getters = {
    allQuestions(state) {
        return state.questions
    },
    questionTableHeaders(state) {
        return state.questionTableHeaders
    }
};

export default {
    state,
    actions,
    mutations,
    getters
}
