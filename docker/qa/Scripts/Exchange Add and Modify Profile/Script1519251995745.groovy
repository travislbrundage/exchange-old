import static com.kms.katalon.core.checkpoint.CheckpointFactory.findCheckpoint
import static com.kms.katalon.core.testcase.TestCaseFactory.findTestCase
import static com.kms.katalon.core.testdata.TestDataFactory.findTestData
import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import com.kms.katalon.core.checkpoint.Checkpoint as Checkpoint
import com.kms.katalon.core.checkpoint.CheckpointFactory as CheckpointFactory
import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as MobileBuiltInKeywords
import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as Mobile
import com.kms.katalon.core.model.FailureHandling as FailureHandling
import com.kms.katalon.core.testcase.TestCase as TestCase
import com.kms.katalon.core.testcase.TestCaseFactory as TestCaseFactory
import com.kms.katalon.core.testdata.TestData as TestData
import com.kms.katalon.core.testdata.TestDataFactory as TestDataFactory
import com.kms.katalon.core.testobject.ObjectRepository as ObjectRepository
import com.kms.katalon.core.testobject.TestObject as TestObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WSBuiltInKeywords
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUiBuiltInKeywords
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import internal.GlobalVariable as GlobalVariable
import org.openqa.selenium.Keys as Keys

WebUI.openBrowser('')

WebUI.navigateToUrl('http://nginx/account/login/?next=/')

WebUI.setText(findTestObject('Page_example.com (1)/input_username'), 'admin')

WebUI.setText(findTestObject('Page_example.com (1)/input_password'), 'exchange')

WebUI.click(findTestObject('Page_example.com (1)/button_Log In'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/a_Admin'))

WebUI.click(findTestObject('Page_exchange Administration  excha/a_Accounts'))

WebUI.click(findTestObject('Page_Select account to change  exch/a_Add account'))

WebUI.click(findTestObject('Page_Add account  exchange Administ/img'))

WebUI.switchToWindowTitle('Add user | exchange Administration')

WebUI.setText(findTestObject('Page_Add user  exchange Administrat/input_username'), 'tester')

WebUI.setText(findTestObject('Page_Add user  exchange Administrat/input_password1'), 'test')

WebUI.setText(findTestObject('Page_Add user  exchange Administrat/input_password2'), 'test')

WebUI.click(findTestObject('Page_Add user  exchange Administrat/input__save'))

WebUI.switchToWindowTitle('Add account | exchange Administration')

WebUI.click(findTestObject('Page_Add account  exchange Administ/a_Accounts'))

WebUI.click(findTestObject('Page_Select account to change  exch/a_View site'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/a_Logout'))

WebUI.click(findTestObject('Page_example.com (1)/button_Log out'))

WebUI.setText(findTestObject('Page_example.com (1)/input_username'), 'tester')

WebUI.setText(findTestObject('Page_example.com (1)/input_password'), 'test')

WebUI.click(findTestObject('Page_example.com (1)/button_Log In'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Welcome - example.com (1)/a_Profile'))

WebUI.click(findTestObject('Page_Profile of tester/a_Edit profile'))

WebUI.setText(findTestObject('Page_example.com (1)/input_first_name'), 'Tester')

WebUI.setText(findTestObject('Page_example.com (1)/input_last_name'), 'Tester')

WebUI.setText(findTestObject('Page_example.com (1)/input_position'), 'Tester')

WebUI.click(findTestObject('Page_example.com (1)/input_btn btn-primary'))

WebUI.click(findTestObject('Page_Profile of Tester (1)/i_fa fa-caret-down'))

WebUI.click(findTestObject('Page_Profile of Tester (1)/a_Logout'))

WebUI.click(findTestObject('Page_example.com (1)/button_Log out'))

WebUI.closeBrowser()

