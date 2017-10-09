<template>
	<div class="checkAnswerPage">
	    <v-layout row wrap>
            <v-flex xs12>
            	<v-select
                     :items="questions"
                     v-model="questionId"
                     label="Выбор вопроса"
                     item-value="id"
                     item-text="question"
                     autocomplete
                ></v-select>
            </v-flex>
        </v-layout>
        <v-layout row>
            <v-flex xs10>
                <v-text-field
                    v-model="sentence"
                    name="input-1"
                    label="Ввод ответа"
                    id="testing"
                ></v-text-field>
            </v-flex>
            <v-flex xs2>
                <v-btn block @click="check">Проверить</v-btn>
            </v-flex>
        </v-layout>
	</div>
</template>
<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
export default{
    created: function() {
        this.$store.commit('load_questions')
    },
    computed: {
        ...mapGetters({
            questions: 'allQuestions',
            answers: 'getAnswers'
        })
    },
    methods: {
    	check(){
    		Vue.http.post('http://localhost:8000/answer/check', {'answer': this.sentence, 'question_id': this.questionId}).then(response => {
				if(response.body){
                	console.log(response.body)
            	}
        	});
    	}
    },
    data(){
    	return {
    		sentence: '',
    		questionId: ''
    	}
    }
}
</script>