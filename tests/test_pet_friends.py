from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password, stored_pet_id
import os
import pytest

pytest.pet_id = '' # создадим переменную для сохранения id животного между тестами

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 при вводе неправильного логина: email=invalid_email """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    # Эта дополнительная проверка на поиск описания ошибки может быть пропущена
    assert 'This user wasn&#x27;t found in database' in result


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 при вводе неправильного пароля: password=invalid_password """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    # Эта дополнительная проверка на поиск описания ошибки может быть пропущена
    assert 'This user wasn&#x27;t found in database' in result


def test_create_pet_simple_valid(name='Tom', animal_type='Cat', age='7'):
    """ Проверяем вызов метода для создания питомца без фото """

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

    # Сохраняем id для запуска следующего теста 'test_set_photo_valid'
    pytest.pet_id = result['id']


def test_set_photo_valid(pet_photo='img/cat1.jpg'):
    """ Проверяем метод добавления фото к ранее созданному питомцу """
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Проверим id если равен False, то подставим заведомо существующий stored_pet_id
    if pytest.pet_id == '':
        pytest.pet_id = stored_pet_id

    status, result = pf.set_photo(auth_key, pytest.pet_id, pet_photo)
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['id'] == pytest.pet_id


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает ошибку при использовании неверного auth_key.
    Для этого сначала получаем api ключ и сохраняем невалидный ключ в переменную auth_key. Далее, используя этот ключ,
    запрашиваем список всех питомцев и проверяем, что возвращается код статуса ошибки 403. """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    auth_key['key'] = '0x000000' # подставим заведомо неправильный ключ аутентификации
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403
    # проверим дополнительное условие
    assert 'Please provide &#x27;auth_key&#x27;' in result


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='img/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "img/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")