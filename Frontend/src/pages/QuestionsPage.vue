<template>
    <div class="questionsPage">
        <v-layout row>
            <v-flex xs10>
                <v-text-field
                        v-model="question"
                        @input="add"
                        name="input-1"
                        label="Ввод вопроса"
                        id="testing">
                </v-text-field>
            </v-flex>
            <v-flex xs2>
                <v-btn block @click="addQuestion">добавить</v-btn>
            </v-flex>
        </v-layout>
        <template>
            <v-data-table
                    :headers="headers"
                    :items="questions"
                    hide-actions
                    class="elevation-1"
            >
                <template slot="items" scope="props">
                    <td>{{ props.item.question }}</td>
                    <td class="text-xs-right">{{ props.item.answerCount }}</td>
                </template>
            </v-data-table>
        </template>
    </div>
</template>

<script>
    import {mapActions, mapGetters, mapState} from 'vuex'

    export default {
        created: function () {
            this.$store.commit('load_questions')
        },
        computed: {
            ...mapGetters({
                questions: 'allQuestions',
                headers: 'questionTableHeaders'
            })
        },
        methods: {
            add(text) {
                this.$store.dispatch('addText', text)
            },
            addQuestion() {
                this.$store.dispatch('addQuestion')
                this.question = ''
            }
        },
        data() {
            return {
                question: ''
            }
        }
    }
</script>