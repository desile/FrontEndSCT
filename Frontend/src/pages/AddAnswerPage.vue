<template>
    <div class="addAnswerPage">
        <v-layout row wrap>
            <v-flex xs12>
                <v-select
                        :items="questions"
                        v-model="questionId"
                        label="Выбор вопроса"
                        item-value="id"
                        item-text="question"
                        @change="selectQuestionEvent"
                        autocomplete
                ></v-select>
            </v-flex>
        </v-layout>
        <v-layout row>
            <v-flex xs10>
                <v-text-field
                        v-model="sentence"
                        name="input-1"
                        label="Ввод предложения"
                        @input="add"
                        id="testing"
                ></v-text-field>
            </v-flex>
            <v-flex xs2>
                <v-btn block @click="parse">Анализ</v-btn>
            </v-flex>
        </v-layout>
        <template>
            <v-data-table
                    v-bind:headers="linksTableHeader"
                    v-bind:items="links"
                    v-model="selectedLinks"
                    select-all
                    hide-actions
                    selected-key="id"
                    no-data-text="Проведите анализ или добавьте слова вручную"
                    class="elevation-1"
            >
                <template slot="items" scope="props">
                    <td class="text-xs-right">
                        <v-checkbox
                                primary
                                v-model="props.selected"
                        ></v-checkbox>
                    </td>
                    <td>{{ props.item.child.word + ' ' + props.item.parent.word }}</td>
                    <td class="text-xs-right">
                        <v-edit-dialog lazy>
                            {{ props.item.weight }}
                            <v-text-field
                                    slot="input"
                                    label="Edit"
                                    v-model="props.item.weight"
                                    single-line counter="counter"
                            ></v-text-field>
                        </v-edit-dialog>
                    </td>
                    <td class="text-xs-right">{{ props.item.link }}</td>
                    <td class="text-xs-right">{{ props.item.synonyms }}</td>
                </template>

                <template slot="footer">
                    <tr>
                        <td style="width:20px"></td>
                        <td style="padding-left: 20px">
                            <v-text-field @keyup.enter="addLink" v-model="newWord" label="Слово"></v-text-field>
                        </td>
                        <td style="padding-left: 10% ;width: 10px">
                            <v-text-field @keyup.enter="addLink" v-model="newWeight" label="Вес"></v-text-field>
                        </td>
                        <td style="padding-left: 3% ;width: 10px">custom</td>
                        <td style="padding-left: 4% ;width: 10px">false</td>
                    </tr>
                </template>
            </v-data-table>
        </template>
        <v-layout row>
            <v-flex xs10></v-flex>
            <v-flex xs2>
                <v-btn block @click="save">сохранить</v-btn>
            </v-flex>
        </v-layout>
        <template>
            <v-data-table
                    :headers="answerTableHeader"
                    :items="answers"
                    hide-actions
                    no-data-text="Ответы отсутствуют"
                    class="elevation-1"
            >
                <template slot="items" scope="props">
                    <td>{{ props.item.answer }}</td>
                    <td class="text-xs-right">{{ props.item.linkCount }}</td>
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
                answers: 'getAnswers'
            })
        },
        methods: {
            add(text) {
                this.$store.dispatch('updateAnswerText', text)
            },
            parse() {
                let self = this
                self.links = []
                self.selectedLinks = []
                this.$http.post('http://localhost:8000/parse', {text: this.sentence}).then(response => {
                    let words = response.body
                    for (var i = 0; i < words.length; i++) {
                        if (words[i]['link_name'] !== 'ROOT') {
                            self.links.push({
                                'id': i,
                                'child': {
                                    'word': words[i]['word'],
                                    'POS': words[i]['pos_tag'],
                                    'normal_form': words[i]['normal_form']
                                },
                                'parent': {
                                    'word': words[parseInt(words[i]['parent_id'])]['word'],
                                    'POS': words[parseInt(words[i]['parent_id'])]['pos_tag'],
                                    'normal_form': words[parseInt(words[i]['parent_id'])]['normal_form']
                                },
                                'link': words[i]['link_name'],
                                'weight': 1.0,
                                'synonyms': false
                            })
                        }
                    }
                    console.log(self.links)
                });
            },
            save(e) {
                this.$store.dispatch('addAnswer', [this.questionId, this.selectedLinks]);
            },
            selectQuestionEvent(e) {
                if (Number.isInteger(e)) { //because change has double emmit with event object
                    this.$store.commit('load_answers', e)
                }
            },
            addLink() {
                this.links.push({
                    //generate uuid
                    words: [this.newWord, ''],
                    weight: this.newWeight || 1.0,
                    link: 'custom',
                    synonyms: false,
                });

                this.newWord = undefined;
                this.newWeight = undefined;
            }
        },

        data() {
            return {
                sentence: '',
                questionId: null,
                answerTableHeader: [
                    {text: 'Ответ', value: 'name', align: 'left'},
                    {text: 'Количество связей', value: 'linksCount'}
                ],
                linksTableHeader: [
                    {text: 'Слова', value: 'words', align: 'left'},
                    {text: 'Вес', value: 'weight'},
                    {text: 'Связь (UD)', value: 'link'},
                    {text: 'Синонимы', value: 'synonyms'}
                ],
                links: [],
                selectedLinks: [],
                newWord: undefined,
                newWeight: undefined
            }
        }
    }

</script>