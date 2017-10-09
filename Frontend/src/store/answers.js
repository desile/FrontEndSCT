import Vue from 'vue';

const state = {
    answer: '',
    answers: [],
};

const actions = {
    addAnswer({commit}, args) {
        Vue.http.post('http://localhost:8000/answers', {
            answer: state.answer,
            question_id: args[0],
            links: args[1]
        }).then(response => {
            if (response.body) {
                //state.questions = response.body
            }
            commit('clear_answer_field');
            commit('load_answers', args[0]);
            args[1] = []
        });
    },
    updateAnswerText({commit}, text) {
        commit('update_answer', text)
    }

};

const mutations = {
    clear_answer_field(state) {
        state.answer = ''
    },
    update_answer(state, update) {
        state.answer = update
    },
    load_answers(state, questionId) {
        Vue.http.get('http://localhost:8000/answers', {params: {'question_id': questionId}}).then(response => {
            if (response.body) {
                state.answers = response.body;
                console.log(state.answers)
            }
        });
    }
};

const getters = {
    getAnswers(state) {
        return state.answers
    },
};

export default {
    state,
    actions,
    mutations,
    getters
}
