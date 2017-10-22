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
        <div v-if="questionId">
            <v-data-table
                    v-bind:headers="relationsTableHeader"
                    v-bind:items="relations"
                    v-model="selectedRelations"
                    hide-actions
                    selected-key="id"
                    no-data-text="Проведите анализ или добавьте связи вручную"
                    class="elevation-1"
            >
                <template slot="items" scope="props">
                    <td>{{ props.item.words.map(w => w['value']).join(' ') }}</td>
                    <td class="text-xs-right">
                        <v-edit-dialog lazy>
                            {{ props.item.weight }}
                            <v-text-field
                                    type="number"
                                    slot="input"
                                    label="Edit"
                                    v-model="props.item.weight"
                                    single-line counter="counter"
                            ></v-text-field>
                        </v-edit-dialog>
                    </td>
                    <td class="text-xs-right">{{ props.item.relation }}</td>
                    <td class="text-xs-right">
                        <v-edit-dialog lazy>
                            {{ props.item.group }}
                            <v-text-field
                                    type="number"
                                    slot="input"
                                    label="Edit"
                                    v-model="props.item.group"
                                    single-line counter="counter"
                            ></v-text-field>
                        </v-edit-dialog>
                    </td>
                </template>

                <!--<template slot="footer">-->
                <!--<tr>-->
                <!--<td style="width:20px"></td>-->
                <!--<td style="padding-left: 20px">-->
                <!--<v-text-field @keyup.enter="addLink" v-model="newWord" label="Слово"></v-text-field>-->
                <!--</td>-->
                <!--<td style="padding-left: 10% ;width: 10px">-->
                <!--<v-text-field @keyup.enter="addLink" v-model="newWeight" label="Вес"></v-text-field>-->
                <!--</td>-->
                <!--<td style="padding-left: 3% ;width: 10px">custom</td>-->
                <!--<td style="padding-left: 4% ;width: 10px">false</td>-->
                <!--</tr>-->
                <!--</template>-->
            </v-data-table>
            <v-layout row>
                <div class="headline" style="color: royalblue; margin-top: 30px">
                    Добавление новых связей
                </div>
            </v-layout>
            <v-layout row>
                <v-flex xs10>
                    <v-text-field
                            v-model="sentence"
                            name="input-1"
                            label="Ввод предложения"
                            id="testing"
                    ></v-text-field>
                </v-flex>
                <v-flex xs2>
                    <v-btn block @click="buildRelations">Анализ</v-btn>
                </v-flex>
            </v-layout>
            <template>
                <div class="text-xs-center">
                    <v-progress-circular indeterminate v-if="loading" v-bind:size="80" v-bind:width="5" style="color: royalblue"></v-progress-circular>
                </div>
                <v-data-table
                        v-if="!loading && questionId"
                        v-bind:headers="relationsTableHeader"
                        v-bind:items="newRelations"
                        v-model="newSelectedRelations"
                        select-all
                        hide-actions
                        selected-key="id"
                        no-data-text="Проведите анализ или добавьте связи вручную"
                        class="elevation-1"
                >
                    <template slot="items" scope="props">
                        <td class="text-xs-right">
                            <v-checkbox
                                    primary
                                    v-model="props.selected"
                            ></v-checkbox>
                        </td>
                        <td>{{ props.item.words.map(w => w['value']).join(' ') }}</td>
                        <td class="text-xs-right">
                            <v-edit-dialog lazy>
                                {{ props.item.weight }}
                                <v-text-field
                                        type="number"
                                        slot="input"
                                        label="Edit"
                                        v-model="props.item.weight"
                                        single-line counter="counter"
                                ></v-text-field>
                            </v-edit-dialog>
                        </td>
                        <td class="text-xs-right">{{ props.item.relation }}</td>
                        <td class="text-xs-right">
                            <v-edit-dialog lazy>
                                {{ props.item.group }}
                                <v-text-field
                                        type="number"
                                        slot="input"
                                        label="Edit"
                                        v-model="props.item.group"
                                        single-line counter="counter"
                                ></v-text-field>
                            </v-edit-dialog>
                        </td>
                    </template>

                    <!--<template slot="footer">-->
                    <!--<tr>-->
                    <!--<td style="width:20px"></td>-->
                    <!--<td style="padding-left: 20px">-->
                    <!--<v-text-field @keyup.enter="addLink" v-model="newWord" label="Слово"></v-text-field>-->
                    <!--</td>-->
                    <!--<td style="padding-left: 10% ;width: 10px">-->
                    <!--<v-text-field @keyup.enter="addLink" v-model="newWeight" label="Вес"></v-text-field>-->
                    <!--</td>-->
                    <!--<td style="padding-left: 3% ;width: 10px">custom</td>-->
                    <!--<td style="padding-left: 4% ;width: 10px">false</td>-->
                    <!--</tr>-->
                    <!--</template>-->
                </v-data-table>
            </template>
            <v-layout row>
                <v-flex xs10></v-flex>
                <v-flex xs2>
                    <v-btn block @click="save">сохранить</v-btn>
                </v-flex>
            </v-layout>
            <v-layout row>
                <div class="headline" style="color: royalblue; margin-bottom: 10px">
                    Список эталонных ответов
                </div>
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
    </div>
</template>

<script>
    import {mapActions, mapGetters, mapState} from 'vuex'

    export default {
        created: function () {
            let self = this
            self.$http.get('http://localhost:8000/questions').then(response => {
                if (response.body) {
                    self.questions = response.body;
                }
            });
        },

        methods: {
            buildRelations(){
                let self = this
                self.newRelations = []
                self.newSelectedRelations = []
                self.loading = true
                this.$http.post('http://localhost:8000/build_relations', {answers: [self.sentence]}).then(response => {
                    self.newRelations = response.body
                    self.loading = false
                })
            },
            save(e) {
                //todo: save
                //this.$store.dispatch('addAnswer', [this.questionId, this.selectedLinks]);
            },
            selectQuestionEvent(questionId) {
                let self = this
                if (Number.isInteger(questionId)) { //because change has double emmit with event object
                    self.$http.get('http://localhost:8000/answers', {params: {'question_id': questionId}}).then(response => {
                        if (response.body) {
                            self.answers = response.body;
                        }
                    });
                    self.$http.post('http://localhost:8000/relations/all', {question_id: questionId}).then(response => {
                        if (response.body) {
                            self.relations = response.body;
                        }
                    })
                }
            },
            addLink() {
                //TODO: add new links and custom words
            }
        },

        data() {
            return {
                sentence: '',
                questionId: null,
                questions: [],
                loading: false,

                answerTableHeader: [
                    {text: 'Ответ', value: 'name', align: 'left'},
                    {text: 'Количество связей', value: 'linksCount'}
                ],
                answers: [],

                relationsTableHeader: [
                    {text: 'Слова', value: 'words', align: 'left'},
                    {text: 'Вес', value: 'weight'},
                    {text: 'Связь (UD)', value: 'relation'},
                    {text: 'Группа', value: 'group'}
                ],
                relations: [],
                selectedRelations: [],

                newRelations: [],
                newSelectedRelations: [],

                newWord: undefined,
                newWeight: undefined
            }
        }
    }

</script>